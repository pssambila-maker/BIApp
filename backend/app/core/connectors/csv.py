"""CSV file connector using DuckDB."""
from typing import Optional
import os

import duckdb
import pandas as pd

from app.core.connectors.base import DataConnector, TableSchema


class CSVConnector(DataConnector):
    """
    Connector for CSV files using DuckDB for efficient querying.

    Config format:
    {
        "file_path": "/path/to/file.csv",
        "delimiter": ",",  # optional
        "has_header": true,  # optional
        "encoding": "utf-8"  # optional
    }
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.file_path = config.get("file_path")
        self.delimiter = config.get("delimiter", ",")
        self.has_header = config.get("has_header", True)
        self.encoding = config.get("encoding", "utf-8")

    async def connect(self) -> bool:
        """
        Establish connection (DuckDB is in-process, so just verify file exists).

        Returns:
            True if file exists and is accessible
        """
        try:
            if not os.path.exists(self.file_path):
                return False

            # Create DuckDB connection
            self._connection = duckdb.connect(":memory:")
            return True
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Close DuckDB connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    async def test_connection(self) -> dict:
        """
        Test connection by attempting to read the CSV file.

        Returns:
            Dictionary with status and message
        """
        try:
            if not os.path.exists(self.file_path):
                return {
                    "status": "error",
                    "message": f"File not found: {self.file_path}"
                }

            # Try to read first row
            if not self._connection:
                await self.connect()

            query = f"""
                SELECT * FROM read_csv_auto(
                    '{self.file_path}',
                    delim='{self.delimiter}',
                    header={str(self.has_header).lower()}
                ) LIMIT 1
            """
            self._connection.execute(query)

            return {
                "status": "success",
                "message": "Successfully connected to CSV file"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

    async def get_tables(self) -> list[TableSchema]:
        """
        Get list of tables (for CSV, this is just the single file).

        Returns:
            List with one TableSchema representing the CSV file
        """
        try:
            if not self._connection:
                await self.connect()

            # Get basic file info
            file_name = os.path.basename(self.file_path)
            table_name = os.path.splitext(file_name)[0]

            # Get row count
            query = f"""
                SELECT COUNT(*) as count FROM read_csv_auto(
                    '{self.file_path}',
                    delim='{self.delimiter}',
                    header={str(self.has_header).lower()}
                )
            """
            result = self._connection.execute(query).fetchone()
            row_count = result[0] if result else 0

            # Get file size
            size_bytes = os.path.getsize(self.file_path)

            return [TableSchema(
                table_name=table_name,
                schema_name=None,
                row_count=row_count,
                size_bytes=size_bytes
            )]
        except Exception:
            return []

    async def get_schema(self, table_name: str, schema_name: Optional[str] = None) -> TableSchema:
        """
        Get schema information for the CSV file.

        Args:
            table_name: Name of the table (ignored for CSV, always reads the file)
            schema_name: Schema name (not applicable for CSV)

        Returns:
            TableSchema with column information
        """
        if not self._connection:
            await self.connect()

        # Use DuckDB's DESCRIBE to get column information
        query = f"""
            DESCRIBE SELECT * FROM read_csv_auto(
                '{self.file_path}',
                delim='{self.delimiter}',
                header={str(self.has_header).lower()}
            )
        """
        result = self._connection.execute(query).fetchall()

        # Convert DuckDB types to standard types
        columns = []
        for row in result:
            col_name = row[0]
            col_type = row[1]

            # Map DuckDB types to standard types
            type_mapping = {
                "BIGINT": "integer",
                "INTEGER": "integer",
                "DOUBLE": "float",
                "VARCHAR": "string",
                "DATE": "date",
                "TIMESTAMP": "timestamp",
                "BOOLEAN": "boolean"
            }

            standard_type = type_mapping.get(col_type.upper(), "string")

            columns.append({
                "name": col_name,
                "type": standard_type,
                "nullable": True  # CSV doesn't have strict nullability
            })

        # Get row count and file size
        tables = await self.get_tables()
        row_count = tables[0].row_count if tables else 0
        size_bytes = tables[0].size_bytes if tables else 0

        file_name = os.path.basename(self.file_path)
        table_name_actual = os.path.splitext(file_name)[0]

        return TableSchema(
            table_name=table_name_actual,
            schema_name=None,
            columns=columns,
            row_count=row_count,
            size_bytes=size_bytes
        )

    async def preview_data(
        self,
        table_name: str,
        schema_name: Optional[str] = None,
        limit: Optional[int] = 100
    ) -> pd.DataFrame:
        """
        Preview data from the CSV file.

        Args:
            table_name: Name of the table (ignored for CSV)
            schema_name: Schema name (not applicable for CSV)
            limit: Maximum number of rows to return (None = all rows)

        Returns:
            Pandas DataFrame with preview data
        """
        if not self._connection:
            await self.connect()

        # Build query with optional limit
        limit_clause = f"LIMIT {limit}" if limit is not None else ""
        query = f"""
            SELECT * FROM read_csv_auto(
                '{self.file_path}',
                delim='{self.delimiter}',
                header={str(self.has_header).lower()}
            ) {limit_clause}
        """

        result = self._connection.execute(query)
        df = result.df()

        return df

    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query against the CSV file.

        Args:
            query: SQL query string (must reference the CSV using read_csv_auto)

        Returns:
            Pandas DataFrame with query results
        """
        if not self._connection:
            await self.connect()

        # Replace table references with read_csv_auto
        # User can write: SELECT * FROM tablename WHERE ...
        # We'll replace with: SELECT * FROM read_csv_auto(...) WHERE ...
        file_name = os.path.basename(self.file_path)
        table_name = os.path.splitext(file_name)[0]

        csv_reader = f"""read_csv_auto(
            '{self.file_path}',
            delim='{self.delimiter}',
            header={str(self.has_header).lower()}
        )"""

        # Simple replacement (in production, use proper SQL parser)
        modified_query = query.replace(f"FROM {table_name}", f"FROM {csv_reader}")

        result = self._connection.execute(modified_query)
        df = result.df()

        return df
