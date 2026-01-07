"""API endpoints for transformation pipelines."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.transformation import TransformationPipeline, TransformationStep, PipelineRun
from app.schemas.transformation import (
    TransformationPipelineCreate,
    TransformationPipelineUpdate,
    TransformationPipelineResponse,
    TransformationPipelineList,
    TransformationStepCreate,
    TransformationStepUpdate,
    TransformationStepResponse,
    PipelineRunResponse,
    PipelineExecuteRequest,
    PipelineExecuteResponse,
)
from app.core.transformation.engine import TransformationEngine

router = APIRouter(tags=["transformations"])


# ==================== Pipeline CRUD ====================

@router.post("/pipelines", response_model=TransformationPipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: TransformationPipelineCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new transformation pipeline."""
    # Create pipeline
    pipeline = TransformationPipeline(
        name=pipeline_data.name,
        description=pipeline_data.description,
        owner_id=current_user.id,
        is_active=pipeline_data.is_active,
        schedule_config=pipeline_data.schedule_config
    )
    db.add(pipeline)
    await db.flush()

    # Add steps
    for step_data in pipeline_data.steps:
        step = TransformationStep(
            pipeline_id=pipeline.id,
            step_order=step_data.step_order,
            step_type=step_data.step_type,
            step_name=step_data.step_name,
            configuration=step_data.configuration,
            output_alias=step_data.output_alias
        )
        db.add(step)

    await db.commit()
    await db.refresh(pipeline)

    # Load with steps
    result = await db.execute(
        select(TransformationPipeline)
        .where(TransformationPipeline.id == pipeline.id)
        .options(selectinload(TransformationPipeline.steps))
    )
    pipeline = result.scalar_one()

    return pipeline


@router.get("/pipelines", response_model=List[TransformationPipelineList])
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all transformation pipelines for the current user."""
    result = await db.execute(
        select(
            TransformationPipeline,
            func.count(TransformationStep.id).label("step_count")
        )
        .outerjoin(TransformationStep, TransformationPipeline.id == TransformationStep.pipeline_id)
        .where(TransformationPipeline.owner_id == current_user.id)
        .group_by(TransformationPipeline.id)
        .order_by(TransformationPipeline.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    pipelines = []
    for pipeline, step_count in result:
        pipelines.append(
            TransformationPipelineList(
                id=pipeline.id,
                name=pipeline.name,
                description=pipeline.description,
                is_active=pipeline.is_active,
                last_run_at=pipeline.last_run_at,
                last_run_status=pipeline.last_run_status,
                step_count=step_count or 0,
                created_at=pipeline.created_at
            )
        )

    return pipelines


@router.get("/pipelines/{pipeline_id}", response_model=TransformationPipelineResponse)
async def get_pipeline(
    pipeline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transformation pipeline."""
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
        .options(selectinload(TransformationPipeline.steps))
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    return pipeline


@router.put("/pipelines/{pipeline_id}", response_model=TransformationPipelineResponse)
async def update_pipeline(
    pipeline_id: UUID,
    pipeline_data: TransformationPipelineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a transformation pipeline."""
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
        .options(selectinload(TransformationPipeline.steps))
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Update fields
    update_data = pipeline_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pipeline, field, value)

    await db.commit()
    await db.refresh(pipeline)

    return pipeline


@router.delete("/pipelines/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a transformation pipeline."""
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    await db.delete(pipeline)
    await db.commit()


# ==================== Pipeline Steps ====================

@router.post("/pipelines/{pipeline_id}/steps", response_model=TransformationStepResponse, status_code=status.HTTP_201_CREATED)
async def add_step(
    pipeline_id: UUID,
    step_data: TransformationStepCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a step to a pipeline."""
    # Verify pipeline ownership
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Create step
    step = TransformationStep(
        pipeline_id=pipeline_id,
        step_order=step_data.step_order,
        step_type=step_data.step_type,
        step_name=step_data.step_name,
        configuration=step_data.configuration,
        output_alias=step_data.output_alias
    )
    db.add(step)
    await db.commit()
    await db.refresh(step)

    return step


@router.put("/pipelines/{pipeline_id}/steps/{step_id}", response_model=TransformationStepResponse)
async def update_step(
    pipeline_id: UUID,
    step_id: UUID,
    step_data: TransformationStepUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a pipeline step."""
    # Verify pipeline ownership
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Get step
    result = await db.execute(
        select(TransformationStep)
        .where(
            TransformationStep.id == step_id,
            TransformationStep.pipeline_id == pipeline_id
        )
    )
    step = result.scalar_one_or_none()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    # Update fields
    update_data = step_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(step, field, value)

    await db.commit()
    await db.refresh(step)

    return step


@router.delete("/pipelines/{pipeline_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_step(
    pipeline_id: UUID,
    step_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a pipeline step."""
    # Verify pipeline ownership
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Get step
    result = await db.execute(
        select(TransformationStep)
        .where(
            TransformationStep.id == step_id,
            TransformationStep.pipeline_id == pipeline_id
        )
    )
    step = result.scalar_one_or_none()

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    await db.delete(step)
    await db.commit()


# ==================== Pipeline Execution ====================

@router.post("/pipelines/{pipeline_id}/execute", response_model=PipelineExecuteResponse)
async def execute_pipeline(
    pipeline_id: UUID,
    execute_request: PipelineExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a transformation pipeline."""
    # Get pipeline with steps
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
        .options(selectinload(TransformationPipeline.steps))
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    if not pipeline.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline is not active"
        )

    # Execute pipeline
    engine = TransformationEngine(db)
    result = await engine.execute_pipeline(
        pipeline,
        limit=execute_request.limit,
        preview_mode=execute_request.preview_mode
    )

    return PipelineExecuteResponse(**result)


@router.post("/pipelines/{pipeline_id}/validate")
async def validate_pipeline(
    pipeline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate a transformation pipeline without executing it."""
    # Get pipeline with steps
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
        .options(selectinload(TransformationPipeline.steps))
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Validate pipeline
    engine = TransformationEngine(db)
    validation_result = await engine.validate_pipeline(pipeline)

    return validation_result


@router.get("/pipelines/{pipeline_id}/runs", response_model=List[PipelineRunResponse])
async def get_pipeline_runs(
    pipeline_id: UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get execution history for a pipeline."""
    # Verify pipeline ownership
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Get runs
    result = await db.execute(
        select(PipelineRun)
        .where(PipelineRun.pipeline_id == pipeline_id)
        .order_by(PipelineRun.started_at.desc())
        .offset(skip)
        .limit(limit)
    )
    runs = result.scalars().all()

    return runs


@router.get("/pipelines/{pipeline_id}/runs/{run_id}", response_model=PipelineRunResponse)
async def get_pipeline_run(
    pipeline_id: UUID,
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific pipeline run."""
    # Verify pipeline ownership
    result = await db.execute(
        select(TransformationPipeline)
        .where(
            TransformationPipeline.id == pipeline_id,
            TransformationPipeline.owner_id == current_user.id
        )
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Get run
    result = await db.execute(
        select(PipelineRun)
        .where(
            PipelineRun.id == run_id,
            PipelineRun.pipeline_id == pipeline_id
        )
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found"
        )

    return run
