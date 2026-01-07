"""Transformation operations for data processing."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.data_source import DataSource
from app.core.connectors import get_connector


class TransformationOperation(ABC):
    """Abstract base class for transformation operations."""

    def __init__(self, db: AsyncSession, intermediate_results: dict[str, pd.DataFrame]):
        """
        Initialize operation.

        Args:
            db: Database session
            intermediate_results: Dictionary of intermediate DataFrames from previous steps
        """
        self.db = db
        self.intermediate_results = intermediate_results

    @abstractmethod
    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Execute the transformation operation.

        Args:
            config: Operation-specific configuration

        Returns:
            Transformed DataFrame
        """
        pass


class SourceOperation(TransformationOperation):
    """Load data from a data source."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Load data from source.

        Config:
            - data_source_id: UUID of data source
            - table_name: Name of table/sheet
            - schema_name: Optional schema name
            - columns: Optional list of columns to load
        """
        data_source_id = UUID(config["data_source_id"])
        table_name = config["table_name"]
        schema_name = config.get("schema_name")
        columns = config.get("columns")

        # Get data source
        result = await self.db.execute(
            select(DataSource).where(DataSource.id == data_source_id)
        )
        data_source = result.scalar_one_or_none()
        if not data_source:
            raise ValueError(f"Data source not found: {data_source_id}")

        # Get connector
        connector = get_connector(data_source)
        await connector.connect()

        try:
            # Load data
            df = await connector.preview_data(table_name, schema_name, limit=None)

            # Select specific columns if requested
            if columns:
                missing_cols = set(columns) - set(df.columns)
                if missing_cols:
                    raise ValueError(f"Columns not found: {missing_cols}")
                df = df[columns]

            return df

        finally:
            await connector.disconnect()


class FilterOperation(TransformationOperation):
    """Filter rows based on conditions."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Filter data.

        Config:
            - conditions: List of conditions [{"column": "age", "operator": ">", "value": 18}]
            - logical_operator: "AND" or "OR"
        """
        # Get input data (from last intermediate result)
        if not self.intermediate_results:
            raise ValueError("No input data for filter operation")

        df = list(self.intermediate_results.values())[-1].copy()
        conditions = config["conditions"]
        logical_operator = config.get("logical_operator", "AND")

        # Build filter mask
        masks = []
        for condition in conditions:
            column = condition["column"]
            operator = condition["operator"]
            value = condition["value"]

            if column not in df.columns:
                raise ValueError(f"Column not found: {column}")

            if operator == "==":
                mask = df[column] == value
            elif operator == "!=":
                mask = df[column] != value
            elif operator == ">":
                mask = df[column] > value
            elif operator == ">=":
                mask = df[column] >= value
            elif operator == "<":
                mask = df[column] < value
            elif operator == "<=":
                mask = df[column] <= value
            elif operator == "in":
                mask = df[column].isin(value)
            elif operator == "not in":
                mask = ~df[column].isin(value)
            elif operator == "contains":
                mask = df[column].astype(str).str.contains(str(value), case=False, na=False)
            elif operator == "startswith":
                mask = df[column].astype(str).str.startswith(str(value), na=False)
            elif operator == "endswith":
                mask = df[column].astype(str).str.endswith(str(value), na=False)
            elif operator == "is null":
                mask = df[column].isnull()
            elif operator == "is not null":
                mask = df[column].notnull()
            else:
                raise ValueError(f"Unknown operator: {operator}")

            masks.append(mask)

        # Combine masks
        if logical_operator.upper() == "AND":
            final_mask = pd.Series([True] * len(df))
            for mask in masks:
                final_mask = final_mask & mask
        else:  # OR
            final_mask = pd.Series([False] * len(df))
            for mask in masks:
                final_mask = final_mask | mask

        return df[final_mask].reset_index(drop=True)


class JoinOperation(TransformationOperation):
    """Join two datasets."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Join datasets.

        Config:
            - left_source: Source alias or "previous"
            - right_source: Source alias
            - join_type: "inner", "left", "right", "full"
            - left_on: Column name
            - right_on: Column name
            - suffix_left: Suffix for duplicate columns from left
            - suffix_right: Suffix for duplicate columns from right
        """
        left_source = config["left_source"]
        right_source = config["right_source"]
        join_type = config.get("join_type", "inner")
        left_on = config["left_on"]
        right_on = config["right_on"]
        suffix_left = config.get("suffix_left", "_left")
        suffix_right = config.get("suffix_right", "_right")

        # Get left DataFrame
        if left_source == "previous":
            left_df = list(self.intermediate_results.values())[-1].copy()
        else:
            if left_source not in self.intermediate_results:
                raise ValueError(f"Left source not found: {left_source}")
            left_df = self.intermediate_results[left_source].copy()

        # Get right DataFrame
        if right_source not in self.intermediate_results:
            raise ValueError(f"Right source not found: {right_source}")
        right_df = self.intermediate_results[right_source].copy()

        # Perform join
        result_df = pd.merge(
            left_df,
            right_df,
            left_on=left_on,
            right_on=right_on,
            how=join_type,
            suffixes=(suffix_left, suffix_right)
        )

        return result_df.reset_index(drop=True)


class AggregateOperation(TransformationOperation):
    """Aggregate data with group by."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Aggregate data.

        Config:
            - group_by: List of column names
            - aggregations: List of {column, function, alias}
                Functions: sum, mean, median, min, max, count, std, var
        """
        if not self.intermediate_results:
            raise ValueError("No input data for aggregate operation")

        df = list(self.intermediate_results.values())[-1].copy()
        group_by = config["group_by"]
        aggregations = config["aggregations"]

        # Validate group_by columns exist
        missing_cols = set(group_by) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Group by columns not found: {missing_cols}")

        # Build aggregation dictionary
        agg_dict = {}
        rename_dict = {}

        for agg in aggregations:
            column = agg["column"]
            function = agg["function"]
            alias = agg.get("alias", f"{column}_{function}")

            if column not in df.columns:
                raise ValueError(f"Column not found: {column}")

            if column not in agg_dict:
                agg_dict[column] = []

            agg_dict[column].append(function)
            rename_dict[(column, function)] = alias

        # Perform aggregation
        result_df = df.groupby(group_by).agg(agg_dict)

        # Flatten multi-level columns and rename
        if isinstance(result_df.columns, pd.MultiIndex):
            result_df.columns = ['_'.join(col).strip() for col in result_df.columns.values]

        result_df = result_df.reset_index()

        # Rename columns based on aliases
        for (col, func), alias in rename_dict.items():
            old_name = f"{col}_{func}"
            if old_name in result_df.columns:
                result_df = result_df.rename(columns={old_name: alias})

        return result_df


class SelectOperation(TransformationOperation):
    """Select and rename columns."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Select columns.

        Config:
            - columns: List of column names to keep
            - rename: Optional dict of {old_name: new_name}
        """
        if not self.intermediate_results:
            raise ValueError("No input data for select operation")

        df = list(self.intermediate_results.values())[-1].copy()
        columns = config["columns"]
        rename = config.get("rename", {})

        # Validate columns exist
        missing_cols = set(columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")

        # Select columns
        df = df[columns]

        # Rename columns if specified
        if rename:
            df = df.rename(columns=rename)

        return df


class SortOperation(TransformationOperation):
    """Sort data by columns."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Sort data.

        Config:
            - columns: List of column names
            - ascending: List of booleans (True=ascending, False=descending)
        """
        if not self.intermediate_results:
            raise ValueError("No input data for sort operation")

        df = list(self.intermediate_results.values())[-1].copy()
        columns = config["columns"]
        ascending = config["ascending"]

        if len(columns) != len(ascending):
            raise ValueError("Length of columns and ascending must match")

        # Validate columns exist
        missing_cols = set(columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")

        return df.sort_values(by=columns, ascending=ascending).reset_index(drop=True)


class UnionOperation(TransformationOperation):
    """Union multiple datasets."""

    async def execute(self, config: dict[str, Any]) -> pd.DataFrame:
        """
        Union datasets.

        Config:
            - sources: List of source aliases
            - remove_duplicates: Boolean
        """
        sources = config["sources"]
        remove_duplicates = config.get("remove_duplicates", True)

        # Get all source DataFrames
        dfs = []
        for source in sources:
            if source not in self.intermediate_results:
                raise ValueError(f"Source not found: {source}")
            dfs.append(self.intermediate_results[source].copy())

        # Union all
        result_df = pd.concat(dfs, ignore_index=True)

        # Remove duplicates if requested
        if remove_duplicates:
            result_df = result_df.drop_duplicates().reset_index(drop=True)

        return result_df
