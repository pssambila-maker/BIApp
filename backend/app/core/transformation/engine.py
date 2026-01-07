"""Transformation engine for executing data pipelines."""
import time
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transformation import TransformationPipeline, TransformationStep, PipelineRun
from app.models.data_source import DataSource
from app.core.transformation.operations import (
    SourceOperation,
    FilterOperation,
    JoinOperation,
    AggregateOperation,
    SelectOperation,
    SortOperation,
    UnionOperation,
)


class TransformationEngine:
    """Engine for executing transformation pipelines."""

    def __init__(self, db: AsyncSession):
        """Initialize transformation engine."""
        self.db = db
        self.operation_map = {
            "source": SourceOperation,
            "filter": FilterOperation,
            "join": JoinOperation,
            "aggregate": AggregateOperation,
            "select": SelectOperation,
            "sort": SortOperation,
            "union": UnionOperation,
        }

    async def execute_pipeline(
        self,
        pipeline: TransformationPipeline,
        limit: Optional[int] = None,
        preview_mode: bool = True
    ) -> dict[str, Any]:
        """
        Execute a transformation pipeline.

        Args:
            pipeline: Pipeline to execute
            limit: Maximum number of rows to return
            preview_mode: If True, don't save results

        Returns:
            Execution result with data and metadata
        """
        # Create pipeline run record
        run = PipelineRun(
            id=uuid4(),
            pipeline_id=pipeline.id,
            status="running",
            started_at=datetime.utcnow(),
            execution_log={"steps": []}
        )
        self.db.add(run)
        await self.db.commit()

        start_time = time.time()
        result_df: Optional[pd.DataFrame] = None
        intermediate_results: dict[str, pd.DataFrame] = {}
        error_message: Optional[str] = None

        try:
            # Execute each step in order
            for step in pipeline.steps:
                step_start = time.time()

                # Get operation class
                operation_class = self.operation_map.get(step.step_type)
                if not operation_class:
                    raise ValueError(f"Unknown step type: {step.step_type}")

                # Create and execute operation
                operation = operation_class(self.db, intermediate_results)
                result_df = await operation.execute(step.configuration)

                # Store intermediate result if alias provided
                if step.output_alias:
                    intermediate_results[step.output_alias] = result_df.copy()

                # Log step execution
                step_log = {
                    "step_order": step.step_order,
                    "step_type": step.step_type,
                    "step_name": step.step_name,
                    "rows_in": len(result_df) if result_df is not None else 0,
                    "rows_out": len(result_df) if result_df is not None else 0,
                    "execution_time": time.time() - step_start,
                    "status": "success"
                }
                run.execution_log["steps"].append(step_log)

            # Apply limit if specified
            if limit and result_df is not None:
                result_df = result_df.head(limit)

            # Update run status
            run.status = "success"
            run.completed_at = datetime.utcnow()
            run.rows_processed = len(result_df) if result_df is not None else 0

            # Update pipeline last run info
            pipeline.last_run_at = datetime.utcnow()
            pipeline.last_run_status = "success"

        except Exception as e:
            error_message = str(e)
            run.status = "failed"
            run.completed_at = datetime.utcnow()
            run.error_message = error_message
            pipeline.last_run_at = datetime.utcnow()
            pipeline.last_run_status = "failed"

        await self.db.commit()

        # Prepare response
        execution_time = time.time() - start_time
        response = {
            "run_id": run.id,
            "status": run.status,
            "rows_processed": run.rows_processed or 0,
            "execution_time_seconds": round(execution_time, 3),
            "error_message": error_message,
        }

        # Include data preview if requested and successful
        if preview_mode and result_df is not None and run.status == "success":
            response["data"] = {
                "columns": result_df.columns.tolist(),
                "rows": result_df.to_dict(orient="records"),
                "row_count": len(result_df)
            }

        return response

    async def validate_pipeline(self, pipeline: TransformationPipeline) -> dict[str, Any]:
        """
        Validate a pipeline without executing it.

        Args:
            pipeline: Pipeline to validate

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        if not pipeline.steps:
            errors.append("Pipeline has no steps")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Check first step is a source
        if pipeline.steps[0].step_type != "source":
            errors.append("First step must be a source")

        # Check step order is sequential
        for i, step in enumerate(pipeline.steps):
            if step.step_order != i:
                errors.append(f"Step order mismatch at position {i}")

        # Validate each step's configuration
        for step in pipeline.steps:
            operation_class = self.operation_map.get(step.step_type)
            if not operation_class:
                errors.append(f"Unknown step type: {step.step_type}")
                continue

            # Basic configuration validation
            if step.step_type == "source":
                if "data_source_id" not in step.configuration:
                    errors.append(f"Step {step.step_order}: Missing data_source_id")
                if "table_name" not in step.configuration:
                    errors.append(f"Step {step.step_order}: Missing table_name")

            elif step.step_type == "filter":
                if "conditions" not in step.configuration:
                    errors.append(f"Step {step.step_order}: Missing conditions")

            elif step.step_type == "join":
                required = ["left_source", "right_source", "left_on", "right_on"]
                for field in required:
                    if field not in step.configuration:
                        errors.append(f"Step {step.step_order}: Missing {field}")

            elif step.step_type == "aggregate":
                if "group_by" not in step.configuration:
                    errors.append(f"Step {step.step_order}: Missing group_by")
                if "aggregations" not in step.configuration:
                    errors.append(f"Step {step.step_order}: Missing aggregations")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
