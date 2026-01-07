"""Abstract base class for data connectors."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime

import pandas as pd


class TableSchema:
    """Schema information for a table."""

    def __init__(
        self,
        table_name: str,
        schema_name: Optional[str] = None,
        columns: Optional[list[dict]] = None,
        row_count: Optional[int] = None,
        size_bytes: Optional[int] = None
    ):
        self.table_name = table_name
        self.schema_name = schema_name
        self.columns = columns or []
        self.row_count = row_count
        self.size_bytes = size_bytes

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "schema_name": self.schema_name,
            "columns": self.columns,
            "row_count": self.row_count,
            "size_bytes": self.size_bytes
        }


class DataConnector(ABC):
    """
    Abstract base class for data source connectors.

    All connectors must implement these methods to provide a consistent interface
    for connecting to different data sources.
    """

    def __init__(self, config: dict):
        """
        Initialize connector with configuration.

        Args:
            config: Connection configuration dictionary
        """
        self.config = config
        self._connection = None

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the data source.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source."""
        pass

    @abstractmethod
    async def test_connection(self) -> dict:
        """
        Test connection to data source.

        Returns:
            Dictionary with status and message
        """
        pass

    @abstractmethod
    async def get_tables(self) -> list[TableSchema]:
        """
        Get list of tables/sheets in the data source.

        Returns:
            List of TableSchema objects
        """
        pass

    @abstractmethod
    async def get_schema(self, table_name: str, schema_name: Optional[str] = None) -> TableSchema:
        """
        Get schema information for a specific table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (for databases that support schemas)

        Returns:
            TableSchema object with column information
        """
        pass

    @abstractmethod
    async def preview_data(
        self,
        table_name: str,
        schema_name: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Preview data from a table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (optional)
            limit: Maximum number of rows to return

        Returns:
            Pandas DataFrame with preview data
        """
        pass

    @abstractmethod
    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query (for database connectors).

        Args:
            query: SQL query string

        Returns:
            Pandas DataFrame with query results
        """
        pass

    async def get_sample_values(
        self,
        table_name: str,
        column_name: str,
        limit: int = 10
    ) -> list[Any]:
        """
        Get sample values for a column (for UI previews).

        Args:
            table_name: Name of the table
            column_name: Name of the column
            limit: Number of sample values

        Returns:
            List of sample values
        """
        try:
            df = await self.preview_data(table_name, limit=limit)
            if column_name in df.columns:
                return df[column_name].dropna().unique()[:limit].tolist()
            return []
        except Exception:
            return []

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._connection:
            # Cleanup will be handled by disconnect()
            pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(config={self.config.get('name', 'unnamed')})>"
