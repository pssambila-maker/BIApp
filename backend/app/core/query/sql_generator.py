"""SQL query generation from semantic layer metadata."""
from typing import List, Dict, Tuple
from uuid import UUID

from app.models.semantic import SemanticEntity
from app.schemas.query_builder import FilterCondition


class SQLGenerator:
    """Generate SQL queries from semantic entity selections."""

    def __init__(self, entity: SemanticEntity):
        """
        Initialize SQL generator with semantic entity.

        Args:
            entity: Semantic entity with dimensions and measures
        """
        self.entity = entity
        self.dimension_map = {d.id: d for d in entity.dimensions}
        self.measure_map = {m.id: m for m in entity.measures}

    def generate_sql(
        self,
        dimension_ids: List[UUID],
        measure_ids: List[UUID],
        filters: List[FilterCondition],
        limit: int = 1000
    ) -> Tuple[str, Dict[str, any]]:
        """
        Generate SQL query from semantic selections.

        Args:
            dimension_ids: List of dimension IDs for GROUP BY
            measure_ids: List of measure IDs for aggregations
            filters: List of filter conditions for WHERE clause
            limit: Maximum number of rows to return

        Returns:
            Tuple of (sql_string, parameters_dict)
        """
        # 1. Build SELECT clause
        select_parts = []

        # Add dimension columns
        for dim_id in dimension_ids:
            dim = self.dimension_map[dim_id]
            select_parts.append(dim.sql_column)

        # Add measure aggregations
        for meas_id in measure_ids:
            meas = self.measure_map[meas_id]
            agg_func = meas.aggregation_function
            base_col = meas.base_column
            alias = meas.name.lower().replace(' ', '_')
            select_parts.append(f"{agg_func}({base_col}) as {alias}")

        select_clause = ", ".join(select_parts)

        # 2. Build FROM clause
        from_clause = self.entity.primary_table

        # 3. Build WHERE clause
        where_parts = []
        params = {}
        for i, filter_cond in enumerate(filters):
            dim = self.dimension_map[filter_cond.dimension_id]
            param_name = f"param_{i}"

            if filter_cond.operator in ("IS NULL", "IS NOT NULL"):
                where_parts.append(f"{dim.sql_column} {filter_cond.operator}")
            elif filter_cond.operator == "IN":
                # Skip if value is None or empty list
                if filter_cond.value is None or (isinstance(filter_cond.value, list) and len(filter_cond.value) == 0):
                    continue
                placeholders = ", ".join([
                    f":param_{i}_{j}"
                    for j in range(len(filter_cond.value))
                ])
                where_parts.append(f"{dim.sql_column} IN ({placeholders})")
                for j, val in enumerate(filter_cond.value):
                    params[f"param_{i}_{j}"] = val
            else:
                # Skip filter if value is None (empty in UI)
                if filter_cond.value is None:
                    continue
                where_parts.append(
                    f"{dim.sql_column} {filter_cond.operator} :{param_name}"
                )
                params[param_name] = filter_cond.value

        where_clause = " AND ".join(where_parts) if where_parts else ""

        # 4. Build GROUP BY clause
        group_by_clause = ""
        if dimension_ids:
            group_by_parts = [
                self.dimension_map[d].sql_column for d in dimension_ids
            ]
            group_by_clause = ", ".join(group_by_parts)

        # 5. Assemble final SQL
        sql_parts = [f"SELECT {select_clause}", f"FROM {from_clause}"]

        if where_clause:
            sql_parts.append(f"WHERE {where_clause}")

        if group_by_clause:
            sql_parts.append(f"GROUP BY {group_by_clause}")

        sql_parts.append(f"LIMIT {limit}")

        sql = "\n".join(sql_parts)

        return sql, params
