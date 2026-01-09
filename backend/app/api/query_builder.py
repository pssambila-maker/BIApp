"""Query Builder API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import io
import json
import time

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.semantic import SemanticEntity
from app.models.query_history import QueryHistory
from app.schemas.query_builder import QueryRequest, QueryResponse
from app.schemas.query_history import QueryHistoryListResponse
from app.core.query.sql_generator import SQLGenerator
from app.core.query.executor import QueryExecutor


router = APIRouter(prefix="/query-builder", tags=["Query Builder"])


@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a query built from semantic selections.

    1. Load entity with dimensions and measures
    2. Generate SQL from selections
    3. Find data source containing entity's table
    4. Execute query
    5. Return results + SQL
    """
    # 1. Load entity with relationships
    result = await db.execute(
        select(SemanticEntity)
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
        .where(
            SemanticEntity.id == request.entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # 2. Validate dimension and measure IDs
    valid_dim_ids = {d.id for d in entity.dimensions}
    valid_meas_ids = {m.id for m in entity.measures}

    if not set(request.dimension_ids).issubset(valid_dim_ids):
        raise HTTPException(status_code=400, detail="Invalid dimension ID")

    if not set(request.measure_ids).issubset(valid_meas_ids):
        raise HTTPException(status_code=400, detail="Invalid measure ID")

    # 3. Generate SQL
    try:
        generator = SQLGenerator(entity)
        sql, params = generator.generate_sql(
            request.dimension_ids,
            request.measure_ids,
            request.filters,
            request.limit or 1000
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate SQL: {str(e)}"
        )

    # 4. Find data source
    executor = QueryExecutor()
    try:
        data_source = await executor.find_data_source(
            entity.primary_table,
            current_user.id,
            db
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find data source: {str(e)}"
        )

    # 5. Execute query and track execution time
    start_time = time.time()
    try:
        df = await executor.execute_query(sql, params, data_source, db)
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Convert DataFrame to JSON-serializable format
        results = df.to_dict('records')
        columns = df.columns.tolist()
        row_count = len(results)

        # 6. Log query execution to history
        try:
            history_entry = QueryHistory(
                owner_id=current_user.id,
                entity_id=request.entity_id,
                query_config={
                    "dimension_ids": [str(d) for d in request.dimension_ids],
                    "measure_ids": [str(m) for m in request.measure_ids],
                    "filters": [f.model_dump() for f in (request.filters or [])],
                    "limit": request.limit or 1000
                },
                generated_sql=sql,
                row_count=row_count,
                execution_time_ms=execution_time_ms,
            )
            db.add(history_entry)
            await db.commit()
        except Exception as log_error:
            # Don't fail the request if logging fails
            print(f"Failed to log query history: {log_error}")
            await db.rollback()

        return QueryResponse(
            columns=columns,
            data=results,
            row_count=row_count,
            generated_sql=sql,
            entity_name=entity.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )


@router.post("/export")
async def export_query_results(
    request: QueryRequest,
    format: str = Query(..., pattern="^(csv|xlsx|json)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export query results in specified format (csv, xlsx, json).

    This endpoint executes the same query logic as /execute but returns
    the results as a downloadable file instead of JSON.
    """
    # 1. Load entity with relationships
    result = await db.execute(
        select(SemanticEntity)
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
        .where(
            SemanticEntity.id == request.entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # 2. Validate dimension and measure IDs
    valid_dim_ids = {d.id for d in entity.dimensions}
    valid_meas_ids = {m.id for m in entity.measures}

    if not set(request.dimension_ids).issubset(valid_dim_ids):
        raise HTTPException(status_code=400, detail="Invalid dimension ID")

    if not set(request.measure_ids).issubset(valid_meas_ids):
        raise HTTPException(status_code=400, detail="Invalid measure ID")

    # 3. Generate SQL
    try:
        generator = SQLGenerator(entity)
        sql, params = generator.generate_sql(
            request.dimension_ids,
            request.measure_ids,
            request.filters,
            request.limit or 1000
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate SQL: {str(e)}"
        )

    # 4. Find data source
    executor = QueryExecutor()
    try:
        data_source = await executor.find_data_source(
            entity.primary_table,
            current_user.id,
            db
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find data source: {str(e)}"
        )

    # 5. Execute query
    try:
        df = await executor.execute_query(sql, params, data_source, db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )

    # 6. Export based on format
    output = io.BytesIO()

    if format == "csv":
        df.to_csv(output, index=False)
        media_type = "text/csv"
        filename = f"{entity.name.replace(' ', '_')}_export.csv"
    elif format == "xlsx":
        df.to_excel(output, index=False, engine="openpyxl")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{entity.name.replace(' ', '_')}_export.xlsx"
    elif format == "json":
        output.write(df.to_json(orient="records", indent=2).encode())
        media_type = "application/json"
        filename = f"{entity.name.replace(' ', '_')}_export.json"

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/history", response_model=QueryHistoryListResponse)
async def get_query_history(
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get query execution history for the current user.

    Returns the last N queries executed, ordered by most recent first.
    """
    result = await db.execute(
        select(QueryHistory)
        .where(QueryHistory.owner_id == current_user.id)
        .order_by(desc(QueryHistory.executed_at))
        .limit(limit)
    )
    history = result.scalars().all()

    return QueryHistoryListResponse(history=list(history), total=len(history))
