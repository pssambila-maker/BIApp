"""Excel file connector using DuckDB and openpyxl."""
from typing import Optional
import os

import duckdb
import pandas as pd

from app.core.connectors.base import DataConnector, TableSchema


class ExcelConnector(DataConnector):
    """
    Connector for Excel files using DuckDB for efficient querying.

    Config format:
    {
        "file_path": "/path/to/file.xlsx",
        "sheet_name": "Sheet1"  # optional, defaults to first sheet
    }
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.file_path = config.get("file_path")
        self.sheet_name = config.get("sheet_name")

    async def connect(self) -> bool:
        """
        Establish connection (verify file exists).

        Returns:
            True if file exists and is accessible
        """
        try:
            if not os.path.exists(self.file_path):
                return False

            # Create DuckDB connection
            self._connection = duckdb.connect(":memory:")

            # Install and load spatial extension for Excel support
            self._connection.execute("INSTALL spatial;")
            self._connection.execute("LOAD spatial;")

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
        Test connection by attempting to read the Excel file.

        Returns:
            Dictionary with status and message
        """
        try:
            if not os.path.exists(self.file_path):
                return {
                    "status": "error",
                    "message": f"File not found: {self.file_path}"
                }

            if not self._connection:
                await self.connect()

            # Try to read first sheet
            # DuckDB doesn't have native Excel support, so we'll use pandas
            try:
                pd.read_excel(self.file_path, nrows=1, sheet_name=self.sheet_name or 0)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Cannot read Excel file: {str(e)}"
                }

            return {
                "status": "success",
                "message": "Successfully connected to Excel file"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

    async def get_tables(self) -> list[TableSchema]:
        """
        Get list of sheets in the Excel file.

        Returns:
            List of TableSchema objects, one per sheet
        """
        try:
            if not self._connection:
                await self.connect()

            # Use pandas to get sheet names
            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names

            tables = []
            for sheet_name in sheet_names:
                # Get row count
                df = pd.read_excel(self.file_path, sheet_name=sheet_name, nrows=0)
                # Read without nrows to get actual count (for small files)
                df_full = pd.read_excel(self.file_path, sheet_name=sheet_name)
                row_count = len(df_full)

                # Get file size (same for all sheets)
                size_bytes = os.path.getsize(self.file_path)

                tables.append(TableSchema(
                    table_name=sheet_name,
                    schema_name=None,
                    row_count=row_count,
                    size_bytes=size_bytes
                ))

            return tables
        except Exception:
            return []

    async def get_schema(self, table_name: str, schema_name: Optional[str] = None) -> TableSchema:
        """
        Get schema information for a specific sheet.

        Args:
            table_name: Name of the sheet
            schema_name: Schema name (not applicable for Excel)

        Returns:
            TableSchema with column information
        """
        if not self._connection:
            await self.connect()

        # Read the sheet to infer schema
        df = pd.read_excel(self.file_path, sheet_name=table_name or self.sheet_name or 0, nrows=100)

        # Infer column types
        columns = []
        for col_name, dtype in df.dtypes.items():
            # Map pandas types to standard types
            type_mapping = {
                "int64": "integer",
                "float64": "float",
                "object": "string",
                "datetime64[ns]": "timestamp",
                "bool": "boolean"
            }

            dtype_str = str(dtype)
            standard_type = type_mapping.get(dtype_str, "string")

            columns.append({
                "name": col_name,
                "type": standard_type,
                "nullable": True
            })

        # Get full row count
        df_full = pd.read_excel(self.file_path, sheet_name=table_name or self.sheet_name or 0)
        row_count = len(df_full)
        size_bytes = os.path.getsize(self.file_path)

        return TableSchema(
            table_name=table_name or self.sheet_name or "Sheet1",
            schema_name=None,
            columns=columns,
            row_count=row_count,
            size_bytes=size_bytes
        )

    async def preview_data(
        self,
        table_name: str,
        schema_name: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Preview data from an Excel sheet.

        Args:
            table_name: Name of the sheet
            schema_name: Schema name (not applicable for Excel)
            limit: Maximum number of rows to return

        Returns:
            Pandas DataFrame with preview data
        """
        if not self._connection:
            await self.connect()

        # Use the provided table_name or fall back to configured sheet_name
        sheet = table_name or self.sheet_name or 0

        df = pd.read_excel(self.file_path, sheet_name=sheet, nrows=limit)

        return df

    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query against the Excel data.

        Note: This loads the entire sheet into memory first, then queries it.
        For large Excel files, consider converting to CSV first.

        Args:
            query: SQL query string

        Returns:
            Pandas DataFrame with query results
        """
        if not self._connection:
            await self.connect()

        # Load the Excel sheet into DuckDB
        sheet = self.sheet_name or 0
        df = pd.read_excel(self.file_path, sheet_name=sheet)

        # Register the DataFrame as a table in DuckDB
        file_name = os.path.basename(self.file_path)
        table_name = os.path.splitext(file_name)[0]

        self._connection.register(table_name, df)

        # Execute the query
        result = self._connection.execute(query)
        result_df = result.df()

        # Unregister the table
        self._connection.unregister(table_name)

        return result_df
