"""Query Builder API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.semantic import SemanticEntity
from app.schemas.query_builder import QueryRequest, QueryResponse
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
    # 1. Load entity
    result = await db.execute(
        select(SemanticEntity)
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

        # Convert DataFrame to JSON-serializable format
        results = df.to_dict('records')
        columns = df.columns.tolist()

        return QueryResponse(
            columns=columns,
            data=results,
            row_count=len(results),
            generated_sql=sql,
            entity_name=entity.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )
