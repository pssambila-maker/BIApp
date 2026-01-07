"""PostgreSQL database connector."""
from typing import Optional

import asyncpg
import pandas as pd

from app.core.connectors.base import DataConnector, TableSchema


class PostgreSQLConnector(DataConnector):
    """
    Connector for PostgreSQL databases.

    Config format:
    {
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "username": "user",
        "password": "pass",
        "schema": "public"  # optional, defaults to public
    }
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 5432)
        self.database = config.get("database")
        self.username = config.get("username")
        self.password = config.get("password")
        self.schema = config.get("schema", "public")

    async def connect(self) -> bool:
        """
        Establish connection to PostgreSQL database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._connection = await asyncpg.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            return True
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Close connection to PostgreSQL."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def test_connection(self) -> dict:
        """
        Test connection to PostgreSQL database.

        Returns:
            Dictionary with status and message
        """
        try:
            if not self._connection:
                success = await self.connect()
                if not success:
                    return {
                        "status": "error",
                        "message": "Failed to establish connection"
                    }

            # Test with a simple query
            result = await self._connection.fetchval("SELECT 1")

            if result == 1:
                return {
                    "status": "success",
                    "message": "Successfully connected to PostgreSQL"
                }
            else:
                return {
                    "status": "error",
                    "message": "Connection test query failed"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

    async def get_tables(self) -> list[TableSchema]:
        """
        Get list of tables in the PostgreSQL database.

        Returns:
            List of TableSchema objects
        """
        try:
            if not self._connection:
                await self.connect()

            query = """
                SELECT
                    table_schema,
                    table_name,
                    (SELECT COUNT(*) FROM information_schema.columns c
                     WHERE c.table_schema = t.table_schema
                     AND c.table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = $1
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """

            rows = await self._connection.fetch(query, self.schema)

            tables = []
            for row in rows:
                # Get row count (can be expensive for large tables)
                try:
                    count_query = f'SELECT COUNT(*) FROM "{row["table_schema"]}"."{row["table_name"]}"'
                    row_count = await self._connection.fetchval(count_query)
                except Exception:
                    row_count = None

                # Get table size
                try:
                    size_query = """
                        SELECT pg_total_relation_size($1::regclass) as size
                    """
                    size_bytes = await self._connection.fetchval(
                        size_query,
                        f'"{row["table_schema"]}"."{row["table_name"]}"'
                    )
                except Exception:
                    size_bytes = None

                tables.append(TableSchema(
                    table_name=row["table_name"],
                    schema_name=row["table_schema"],
                    row_count=row_count,
                    size_bytes=size_bytes
                ))

            return tables
        except Exception:
            return []

    async def get_schema(self, table_name: str, schema_name: Optional[str] = None) -> TableSchema:
        """
        Get schema information for a specific table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (defaults to configured schema)

        Returns:
            TableSchema with column information
        """
        if not self._connection:
            await self.connect()

        schema = schema_name or self.schema

        # Get column information
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        """

        rows = await self._connection.fetch(query, schema, table_name)

        columns = []
        for row in rows:
            # Map PostgreSQL types to standard types
            pg_type = row["data_type"]
            type_mapping = {
                "integer": "integer",
                "bigint": "integer",
                "smallint": "integer",
                "numeric": "float",
                "real": "float",
                "double precision": "float",
                "character varying": "string",
                "character": "string",
                "text": "string",
                "date": "date",
                "timestamp without time zone": "timestamp",
                "timestamp with time zone": "timestamp",
                "boolean": "boolean",
                "json": "json",
                "jsonb": "json",
                "uuid": "string"
            }

            standard_type = type_mapping.get(pg_type, "string")

            columns.append({
                "name": row["column_name"],
                "type": standard_type,
                "nullable": row["is_nullable"] == "YES",
                "default": row["column_default"]
            })

        # Get row count
        try:
            count_query = f'SELECT COUNT(*) FROM "{schema}"."{table_name}"'
            row_count = await self._connection.fetchval(count_query)
        except Exception:
            row_count = None

        # Get table size
        try:
            size_query = "SELECT pg_total_relation_size($1::regclass) as size"
            size_bytes = await self._connection.fetchval(size_query, f'"{schema}"."{table_name}"')
        except Exception:
            size_bytes = None

        return TableSchema(
            table_name=table_name,
            schema_name=schema,
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
        Preview data from a PostgreSQL table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (defaults to configured schema)
            limit: Maximum number of rows to return

        Returns:
            Pandas DataFrame with preview data
        """
        if not self._connection:
            await self.connect()

        schema = schema_name or self.schema

        query = f'SELECT * FROM "{schema}"."{table_name}" LIMIT $1'
        rows = await self._connection.fetch(query, limit)

        # Convert to DataFrame
        if rows:
            df = pd.DataFrame([dict(row) for row in rows])
        else:
            df = pd.DataFrame()

        return df

    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query against PostgreSQL.

        Args:
            query: SQL query string

        Returns:
            Pandas DataFrame with query results
        """
        if not self._connection:
            await self.connect()

        rows = await self._connection.fetch(query)

        # Convert to DataFrame
        if rows:
            df = pd.DataFrame([dict(row) for row in rows])
        else:
            df = pd.DataFrame()

        return df
