"""MySQL database connector."""
from typing import Optional

import aiomysql
import pandas as pd

from app.core.connectors.base import DataConnector, TableSchema


class MySQLConnector(DataConnector):
    """
    Connector for MySQL databases.

    Config format:
    {
        "host": "localhost",
        "port": 3306,
        "database": "mydb",
        "username": "user",
        "password": "pass"
    }
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 3306)
        self.database = config.get("database")
        self.username = config.get("username")
        self.password = config.get("password")

    async def connect(self) -> bool:
        """
        Establish connection to MySQL database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._connection = await aiomysql.connect(
                host=self.host,
                port=self.port,
                db=self.database,
                user=self.username,
                password=self.password,
                autocommit=True
            )
            return True
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Close connection to MySQL."""
        if self._connection:
            self._connection.close()
            self._connection = None

    async def test_connection(self) -> dict:
        """
        Test connection to MySQL database.

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
            async with self._connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()

                if result and result[0] == 1:
                    return {
                        "status": "success",
                        "message": "Successfully connected to MySQL"
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
        Get list of tables in the MySQL database.

        Returns:
            List of TableSchema objects
        """
        try:
            if not self._connection:
                await self.connect()

            query = """
                SELECT
                    TABLE_NAME,
                    TABLE_SCHEMA,
                    TABLE_ROWS,
                    DATA_LENGTH + INDEX_LENGTH as size_bytes
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """

            async with self._connection.cursor() as cursor:
                await cursor.execute(query, (self.database,))
                rows = await cursor.fetchall()

                tables = []
                for row in rows:
                    tables.append(TableSchema(
                        table_name=row[0],
                        schema_name=row[1],
                        row_count=row[2],
                        size_bytes=row[3]
                    ))

                return tables
        except Exception:
            return []

    async def get_schema(self, table_name: str, schema_name: Optional[str] = None) -> TableSchema:
        """
        Get schema information for a specific table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (defaults to configured database)

        Returns:
            TableSchema with column information
        """
        if not self._connection:
            await self.connect()

        schema = schema_name or self.database

        # Get column information
        query = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """

        async with self._connection.cursor() as cursor:
            await cursor.execute(query, (schema, table_name))
            rows = await cursor.fetchall()

            columns = []
            for row in rows:
                # Map MySQL types to standard types
                mysql_type = row[1]
                type_mapping = {
                    "int": "integer",
                    "tinyint": "integer",
                    "smallint": "integer",
                    "mediumint": "integer",
                    "bigint": "integer",
                    "decimal": "float",
                    "float": "float",
                    "double": "float",
                    "varchar": "string",
                    "char": "string",
                    "text": "string",
                    "mediumtext": "string",
                    "longtext": "string",
                    "date": "date",
                    "datetime": "timestamp",
                    "timestamp": "timestamp",
                    "tinyint(1)": "boolean",
                    "json": "json"
                }

                standard_type = type_mapping.get(mysql_type, "string")

                columns.append({
                    "name": row[0],
                    "type": standard_type,
                    "nullable": row[2] == "YES",
                    "default": row[3]
                })

            # Get row count and size
            table_query = """
                SELECT TABLE_ROWS, DATA_LENGTH + INDEX_LENGTH as size_bytes
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            await cursor.execute(table_query, (schema, table_name))
            table_info = await cursor.fetchone()

            row_count = table_info[0] if table_info else None
            size_bytes = table_info[1] if table_info else None

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
        Preview data from a MySQL table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (defaults to configured database)
            limit: Maximum number of rows to return

        Returns:
            Pandas DataFrame with preview data
        """
        if not self._connection:
            await self.connect()

        schema = schema_name or self.database

        query = f"SELECT * FROM `{schema}`.`{table_name}` LIMIT %s"

        async with self._connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (limit,))
            rows = await cursor.fetchall()

            # Convert to DataFrame
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame()

            return df

    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query against MySQL.

        Args:
            query: SQL query string

        Returns:
            Pandas DataFrame with query results
        """
        if not self._connection:
            await self.connect()

        async with self._connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()

            # Convert to DataFrame
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame()

            return df
