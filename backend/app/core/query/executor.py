"""Query execution against data sources."""
from uuid import UUID
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
from fastapi import HTTPException

from app.models.data_source import DataSource
from app.core.connectors import get_connector


class QueryExecutor:
    """Execute queries against data sources."""

    async def find_data_source(
        self,
        primary_table: str,
        user_id: UUID,
        db: AsyncSession
    ) -> DataSource:
        """
        Find data source that contains the entity's primary_table.

        Strategy:
        1. Query all user's data sources
        2. Check schema_metadata.tables for matching table_name
        3. Return the first match (prefer certified sources)

        Args:
            primary_table: Table name from semantic entity
            user_id: Current user ID
            db: Database session

        Returns:
            DataSource containing the table

        Raises:
            HTTPException: If no data source found
        """
        result = await db.execute(
            select(DataSource)
            .where(DataSource.owner_id == user_id)
            .order_by(
                DataSource.is_certified.desc(),
                DataSource.created_at.desc()
            )
        )
        data_sources = result.scalars().all()

        for ds in data_sources:
            if ds.schema_metadata and 'tables' in ds.schema_metadata:
                for table in ds.schema_metadata['tables']:
                    if table['table_name'] == primary_table:
                        return ds

        raise HTTPException(
            status_code=404,
            detail=f"No data source found containing table '{primary_table}'"
        )

    async def execute_query(
        self,
        sql: str,
        params: Dict[str, any],
        data_source: DataSource,
        db: AsyncSession
    ) -> pd.DataFrame:
        """
        Execute SQL query against data source.

        Args:
            sql: SQL query string with parameter placeholders
            params: Parameter values for query
            data_source: Data source to execute against
            db: Database session

        Returns:
            Pandas DataFrame with results

        Raises:
            Exception: If query execution fails
        """
        connector = get_connector(data_source)

        # For parameterized queries, we need to replace :param with actual values
        # This is connector-specific - some use %s, some use ?, some use :name

        # For now, use simple string replacement (will improve for production)
        formatted_sql = sql
        for param_name, param_value in params.items():
            if isinstance(param_value, str):
                formatted_sql = formatted_sql.replace(
                    f":{param_name}",
                    f"'{param_value}'"
                )
            else:
                formatted_sql = formatted_sql.replace(
                    f":{param_name}",
                    str(param_value)
                )

        df = await connector.execute_query(formatted_sql)
        return df
