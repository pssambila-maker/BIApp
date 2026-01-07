"""Data source API endpoints."""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.data_source import DataSource, DataSourceTable
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    DataSourceTableResponse,
    ConnectionTestResponse,
    DataPreviewResponse,
)
from app.core.connectors import (
    CSVConnector,
    ExcelConnector,
    PostgreSQLConnector,
    MySQLConnector,
)

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


def get_connector(data_source: DataSource):
    """
    Factory function to create appropriate connector based on data source type.

    Args:
        data_source: DataSource model instance

    Returns:
        Connector instance
    """
    connector_map = {
        "csv": CSVConnector,
        "excel": ExcelConnector,
        "postgresql": PostgreSQLConnector,
        "mysql": MySQLConnector,
    }

    connector_class = connector_map.get(data_source.type)
    if not connector_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported data source type: {data_source.type}"
        )

    return connector_class(data_source.connection_config)


@router.post("/", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    data_source_in: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DataSource:
    """
    Create a new data source connection.

    Args:
        data_source_in: Data source creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created data source
    """
    # Create data source
    data_source = DataSource(
        name=data_source_in.name,
        type=data_source_in.type,
        connection_config=data_source_in.connection_config,
        description=data_source_in.description,
        owner_id=current_user.id
    )

    db.add(data_source)
    await db.commit()
    await db.refresh(data_source)

    return data_source


@router.get("/", response_model=list[DataSourceResponse])
async def list_data_sources(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[DataSource]:
    """
    List all data sources for the current user.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of data sources
    """
    result = await db.execute(
        select(DataSource)
        .where(DataSource.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    data_sources = result.scalars().all()
    return list(data_sources)


@router.get("/{data_source_id}", response_model=DataSourceResponse)
async def get_data_source(
    data_source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DataSource:
    """
    Get a specific data source by ID.

    Args:
        data_source_id: Data source UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Data source details
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    return data_source


@router.put("/{data_source_id}", response_model=DataSourceResponse)
async def update_data_source(
    data_source_id: UUID,
    data_source_in: DataSourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DataSource:
    """
    Update a data source.

    Args:
        data_source_id: Data source UUID
        data_source_in: Data source update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated data source
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    # Update fields
    update_data = data_source_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(data_source, field, value)

    await db.commit()
    await db.refresh(data_source)

    return data_source


@router.delete("/{data_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_source(
    data_source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a data source.

    Args:
        data_source_id: Data source UUID
        db: Database session
        current_user: Current authenticated user
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    await db.delete(data_source)
    await db.commit()


@router.post("/{data_source_id}/test", response_model=ConnectionTestResponse)
async def test_data_source_connection(
    data_source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, str]:
    """
    Test connection to a data source.

    Args:
        data_source_id: Data source UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Connection test result
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    # Create connector and test connection
    connector = get_connector(data_source)

    try:
        test_result = await connector.test_connection()
        await connector.disconnect()
        return test_result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }


@router.get("/{data_source_id}/tables", response_model=list[DataSourceTableResponse])
async def get_data_source_tables(
    data_source_id: UUID,
    refresh: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[dict[str, Any]]:
    """
    Get list of tables/sheets in a data source.

    Args:
        data_source_id: Data source UUID
        refresh: Whether to refresh schema from source
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of tables
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    # If refresh or no cached tables, fetch from source
    if refresh or not data_source.schema_metadata:
        connector = get_connector(data_source)

        try:
            await connector.connect()
            tables = await connector.get_tables()
            await connector.disconnect()

            # Convert to dict format
            tables_data = [table.to_dict() for table in tables]

            # Update schema metadata in database
            data_source.schema_metadata = {"tables": tables_data}
            await db.commit()

            return tables_data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch tables: {str(e)}"
            )
    else:
        # Return cached tables
        return data_source.schema_metadata.get("tables", [])


@router.get("/{data_source_id}/tables/{table_name}/schema", response_model=DataSourceTableResponse)
async def get_table_schema(
    data_source_id: UUID,
    table_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Get schema information for a specific table.

    Args:
        data_source_id: Data source UUID
        table_name: Name of the table
        db: Database session
        current_user: Current authenticated user

    Returns:
        Table schema information
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    connector = get_connector(data_source)

    try:
        await connector.connect()
        schema = await connector.get_schema(table_name)
        await connector.disconnect()

        return schema.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schema: {str(e)}"
        )


@router.get("/{data_source_id}/tables/{table_name}/preview", response_model=DataPreviewResponse)
async def preview_table_data(
    data_source_id: UUID,
    table_name: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Preview data from a table.

    Args:
        data_source_id: Data source UUID
        table_name: Name of the table
        limit: Maximum number of rows to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        Preview data
    """
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.owner_id == current_user.id
        )
    )
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )

    connector = get_connector(data_source)

    try:
        await connector.connect()
        df = await connector.preview_data(table_name, limit=limit)
        await connector.disconnect()

        # Convert DataFrame to JSON-serializable format
        return {
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient="records"),
            "row_count": len(df)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview data: {str(e)}"
        )
