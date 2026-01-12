"""Scheduled reports API endpoints."""
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.scheduled_report import ScheduledReport, ReportExecution
from app.models.dashboard import Dashboard
from app.models.saved_query import SavedQuery
from app.schemas.scheduled_report import (
    ScheduledReportCreate,
    ScheduledReportUpdate,
    ScheduledReportResponse,
    ScheduledReportListResponse,
    ReportExecutionResponse,
    ExecutionHistoryResponse,
    ManualRunResponse,
    TestRunResponse
)
from app.services.schedule_service import ScheduleService
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from app.api.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/scheduled-reports", tags=["scheduled-reports"])


@router.post("", response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_report(
    report_data: ScheduledReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new scheduled report.

    The report will be automatically executed based on the schedule configuration.
    Must have either a dashboard_id or saved_query_id (but not both).
    """
    # Verify ownership of source (dashboard or saved query)
    if report_data.dashboard_id:
        result = await db.execute(
            select(Dashboard).where(
                Dashboard.id == report_data.dashboard_id,
                Dashboard.owner_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found or access denied"
            )

    if report_data.saved_query_id:
        result = await db.execute(
            select(SavedQuery).where(
                SavedQuery.id == report_data.saved_query_id,
                SavedQuery.owner_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved query not found or access denied"
            )

    # Calculate initial next_run_at
    schedule_service = ScheduleService()
    try:
        next_run_at = schedule_service.calculate_next_run(report_data.schedule_config.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid schedule configuration: {str(e)}"
        )

    # Create scheduled report
    scheduled_report = ScheduledReport(
        owner_id=current_user.id,
        name=report_data.name,
        description=report_data.description,
        dashboard_id=report_data.dashboard_id,
        saved_query_id=report_data.saved_query_id,
        schedule_config=report_data.schedule_config.model_dump(),
        recipients=report_data.recipients,
        formats=report_data.formats,
        email_subject=report_data.email_subject,
        email_body=report_data.email_body,
        is_active=report_data.is_active,
        next_run_at=next_run_at
    )

    db.add(scheduled_report)
    await db.commit()
    await db.refresh(scheduled_report)

    return scheduled_report


@router.get("", response_model=ScheduledReportListResponse)
async def list_scheduled_reports(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all scheduled reports for the current user.

    Supports filtering by active status and pagination.
    """
    # Build query
    query = select(ScheduledReport).where(ScheduledReport.owner_id == current_user.id)

    if is_active is not None:
        query = query.where(ScheduledReport.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(ScheduledReport).where(
        ScheduledReport.owner_id == current_user.id
    )
    if is_active is not None:
        count_query = count_query.where(ScheduledReport.is_active == is_active)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(desc(ScheduledReport.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()

    return ScheduledReportListResponse(
        total=total,
        reports=reports
    )


@router.get("/{report_id}", response_model=ScheduledReportResponse)
async def get_scheduled_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific scheduled report by ID.

    Includes the last execution summary if available.
    """
    result = await db.execute(
        select(ScheduledReport)
        .options(selectinload(ScheduledReport.executions).limit(1))
        .where(
            ScheduledReport.id == report_id,
            ScheduledReport.owner_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    # Manually set last_execution from the loaded executions
    response_data = ScheduledReportResponse.model_validate(report)
    if report.executions:
        response_data.last_execution = ReportExecutionResponse.model_validate(report.executions[0])

    return response_data


@router.put("/{report_id}", response_model=ScheduledReportResponse)
async def update_scheduled_report(
    report_id: UUID,
    report_update: ScheduledReportUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing scheduled report.

    If schedule_config is updated, next_run_at will be recalculated.
    """
    # Get existing report
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.id == report_id,
            ScheduledReport.owner_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    # Update fields
    update_data = report_update.model_dump(exclude_unset=True)

    # If schedule changed, recalculate next_run_at
    if 'schedule_config' in update_data:
        schedule_service = ScheduleService()
        try:
            next_run_at = schedule_service.calculate_next_run(update_data['schedule_config'])
            report.next_run_at = next_run_at
            report.schedule_config = update_data['schedule_config']
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid schedule configuration: {str(e)}"
            )
        del update_data['schedule_config']

    # Update other fields
    for field, value in update_data.items():
        setattr(report, field, value)

    await db.commit()
    await db.refresh(report)

    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a scheduled report.

    This will also delete all associated execution history (cascade delete).
    """
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.id == report_id,
            ScheduledReport.owner_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    await db.delete(report)
    await db.commit()


@router.post("/{report_id}/run", response_model=ManualRunResponse)
async def run_scheduled_report_now(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger a scheduled report to run immediately.

    This queues the report execution as a Celery task and returns immediately.
    Use the task_id to check execution status.
    """
    # Verify report exists and user owns it
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.id == report_id,
            ScheduledReport.owner_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    # TODO: Queue Celery task when implemented
    # from app.tasks.reports import run_scheduled_report_task
    # task = run_scheduled_report_task.delay(str(report_id))

    return ManualRunResponse(
        task_id=None,  # Will be task.id when Celery implemented
        status="queued",
        message="Report execution queued. This feature will be fully enabled when Celery tasks are implemented.",
        scheduled_report_id=report_id
    )


@router.post("/{report_id}/test", response_model=TestRunResponse)
async def test_scheduled_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Test a scheduled report by running it immediately and sending to current user only.

    This executes synchronously (not via Celery) and overrides recipients with current user's email.
    Useful for testing before enabling the schedule.
    """
    start_time = time.time()

    # Get report
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.id == report_id,
            ScheduledReport.owner_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    # Verify user has email configured
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your user account has no email address. Cannot send test report."
        )

    # Initialize services
    report_service = ReportService()
    email_service = EmailService()

    try:
        # Execute query
        if report.dashboard_id:
            widget_results = await report_service.execute_dashboard_queries(
                report.dashboard_id,
                current_user.id,
                db
            )
            # For dashboard, combine all widget data (simplified)
            import pandas as pd
            combined_data = pd.concat(widget_results.values(), ignore_index=True) if widget_results else pd.DataFrame()
        elif report.saved_query_id:
            combined_data = await report_service.execute_saved_query(
                report.saved_query_id,
                current_user.id,
                db
            )
        else:
            raise ValueError("Report has no dashboard_id or saved_query_id")

        row_count = len(combined_data)

        # Generate files
        test_dir = Path(settings.export_dir) / "reports" / "test" / str(report_id)
        test_dir.mkdir(parents=True, exist_ok=True)

        generated_files = await report_service.generate_all_formats(
            data=combined_data,
            formats=report.formats,
            report_name=f"test_{report.name.replace(' ', '_')}",
            report_dir=test_dir
        )

        # Send email to current user
        email_subject = report.email_subject or f"Test: {report.name}"
        email_body = report.email_body or report_service.generate_html_email(
            combined_data,
            title=report.name
        )

        attachments = [path for path in generated_files.values() if 'html' not in str(path).lower()]

        send_result = await email_service.send_report_email(
            user_id=current_user.id,
            recipients=[current_user.email],
            subject=f"[TEST] {email_subject}",
            body_html=email_body,
            attachments=attachments,
            db=db
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        return TestRunResponse(
            status="success",
            message=f"Test report executed successfully and sent to {current_user.email}",
            generated_files={k: str(v) for k, v in generated_files.items()},
            sent_to=[current_user.email],
            execution_time_ms=execution_time_ms,
            row_count=row_count
        )

    except ValueError as e:
        return TestRunResponse(
            status="error",
            message=str(e),
            error_message=str(e)
        )
    except Exception as e:
        return TestRunResponse(
            status="error",
            message=f"Test execution failed: {str(e)}",
            error_message=str(e)
        )


@router.get("/{report_id}/executions", response_model=ExecutionHistoryResponse)
async def get_execution_history(
    report_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get execution history for a scheduled report.

    Returns paginated list of past executions with details.
    """
    # Verify report ownership
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.id == report_id,
            ScheduledReport.owner_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(ReportExecution).where(
            ReportExecution.scheduled_report_id == report_id
        )
    )
    total = count_result.scalar()

    # Get executions
    exec_result = await db.execute(
        select(ReportExecution)
        .where(ReportExecution.scheduled_report_id == report_id)
        .order_by(desc(ReportExecution.created_at))
        .offset(offset)
        .limit(limit)
    )
    executions = exec_result.scalars().all()

    return ExecutionHistoryResponse(
        total=total,
        executions=executions
    )
