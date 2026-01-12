"""Celery tasks for scheduled reports."""
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from uuid import UUID

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.scheduled_report import ScheduledReport, ReportExecution
from app.services.schedule_service import ScheduleService
from app.services.report_service import ReportService
from app.services.email_service import EmailService


@shared_task(
    bind=True,
    name='app.tasks.reports.run_scheduled_report_task',
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def run_scheduled_report_task(self, scheduled_report_id: str):
    """
    Execute a specific scheduled report.

    This is the main worker task that:
    1. Loads report configuration
    2. Executes query (Dashboard or SavedQuery)
    3. Generates files (Excel, CSV, PDF)
    4. Sends email with attachments
    5. Creates execution record
    6. Updates next_run_at

    Args:
        scheduled_report_id: UUID of the scheduled report to execute

    Returns:
        Dict with execution summary
    """
    # Run async code in sync context
    return asyncio.run(_execute_report_async(scheduled_report_id, triggered_by='schedule'))


async def _execute_report_async(scheduled_report_id: str, triggered_by: str = 'schedule') -> Dict[str, Any]:
    """
    Async implementation of report execution.

    Args:
        scheduled_report_id: UUID of report to execute
        triggered_by: How execution was triggered ('schedule', 'manual', 'test')

    Returns:
        Dict with execution results
    """
    start_time = time.time()
    execution_id = None

    async with AsyncSessionLocal() as db:
        try:
            # 1. Load scheduled report
            result = await db.execute(
                select(ScheduledReport).where(
                    ScheduledReport.id == UUID(scheduled_report_id)
                )
            )
            report = result.scalar_one_or_none()

            if not report:
                return {
                    "status": "error",
                    "message": f"Scheduled report {scheduled_report_id} not found",
                    "scheduled_report_id": scheduled_report_id
                }

            if not report.is_active and triggered_by == 'schedule':
                return {
                    "status": "skipped",
                    "message": "Report is not active",
                    "scheduled_report_id": scheduled_report_id
                }

            # 2. Create execution record (status='running')
            execution = ReportExecution(
                scheduled_report_id=report.id,
                status='running',
                triggered_by=triggered_by
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            execution_id = execution.id

            # 3. Initialize services
            report_service = ReportService()
            email_service = EmailService()
            schedule_service = ScheduleService()

            # 4. Execute query
            try:
                if report.dashboard_id:
                    widget_results = await report_service.execute_dashboard_queries(
                        report.dashboard_id,
                        report.owner_id,
                        db
                    )
                    # Combine all widget data
                    import pandas as pd
                    if widget_results:
                        data = pd.concat(widget_results.values(), ignore_index=True)
                    else:
                        data = pd.DataFrame()
                elif report.saved_query_id:
                    data = await report_service.execute_saved_query(
                        report.saved_query_id,
                        report.owner_id,
                        db
                    )
                else:
                    raise ValueError("Report has neither dashboard_id nor saved_query_id")

                row_count = len(data)

            except Exception as e:
                # Mark execution as failed
                execution.status = 'failed'
                execution.error_message = f"Query execution failed: {str(e)}"
                execution.execution_time_ms = int((time.time() - start_time) * 1000)
                await db.commit()

                # Still update next_run_at so we don't skip future executions
                if triggered_by == 'schedule':
                    report.next_run_at = schedule_service.calculate_next_run(
                        report.schedule_config,
                        datetime.utcnow()
                    )
                    report.last_run_at = datetime.utcnow()
                    await db.commit()

                return {
                    "status": "failed",
                    "message": f"Query execution failed: {str(e)}",
                    "execution_id": str(execution_id)
                }

            # 5. Generate files
            try:
                report_dir = Path(settings.export_dir) / "reports" / str(report.id) / str(execution.id)
                report_dir.mkdir(parents=True, exist_ok=True)

                report_name = report.name.replace(' ', '_')
                generated_files = await report_service.generate_all_formats(
                    data=data,
                    formats=report.formats,
                    report_name=report_name,
                    report_dir=report_dir
                )

            except Exception as e:
                # Mark execution as failed
                execution.status = 'failed'
                execution.error_message = f"File generation failed: {str(e)}"
                execution.row_count = row_count
                execution.execution_time_ms = int((time.time() - start_time) * 1000)
                await db.commit()

                # Update next_run_at
                if triggered_by == 'schedule':
                    report.next_run_at = schedule_service.calculate_next_run(
                        report.schedule_config,
                        datetime.utcnow()
                    )
                    report.last_run_at = datetime.utcnow()
                    await db.commit()

                return {
                    "status": "failed",
                    "message": f"File generation failed: {str(e)}",
                    "execution_id": str(execution_id),
                    "row_count": row_count
                }

            # 6. Send email
            try:
                # Prepare email subject and body
                email_subject = report.email_subject or f"{report.name} - {datetime.utcnow().strftime('%Y-%m-%d')}"
                email_body = report.email_body or report_service.generate_html_email(
                    data,
                    title=report.name
                )

                # Get file attachments (exclude HTML if it's in formats)
                attachments = [
                    path for fmt, path in generated_files.items()
                    if fmt != 'html'
                ]

                # Send email
                send_result = await email_service.send_report_email(
                    user_id=report.owner_id,
                    recipients=report.recipients,
                    subject=email_subject,
                    body_html=email_body,
                    attachments=attachments,
                    db=db
                )

                # Mark execution as successful
                execution.status = 'success'
                execution.generated_files = {fmt: str(path) for fmt, path in generated_files.items()}
                execution.sent_to = send_result['sent_to']
                execution.row_count = row_count
                execution.execution_time_ms = int((time.time() - start_time) * 1000)
                await db.commit()

            except Exception as e:
                # Mark as partial success (files generated but email failed)
                execution.status = 'partial'
                execution.generated_files = {fmt: str(path) for fmt, path in generated_files.items()}
                execution.error_message = f"Email sending failed: {str(e)}"
                execution.row_count = row_count
                execution.execution_time_ms = int((time.time() - start_time) * 1000)
                await db.commit()

                # Update next_run_at
                if triggered_by == 'schedule':
                    report.next_run_at = schedule_service.calculate_next_run(
                        report.schedule_config,
                        datetime.utcnow()
                    )
                    report.last_run_at = datetime.utcnow()
                    await db.commit()

                return {
                    "status": "partial",
                    "message": f"Files generated but email failed: {str(e)}",
                    "execution_id": str(execution_id),
                    "row_count": row_count,
                    "files": execution.generated_files
                }

            # 7. Update next_run_at and last_run_at
            if triggered_by == 'schedule':
                report.next_run_at = schedule_service.calculate_next_run(
                    report.schedule_config,
                    datetime.utcnow()
                )
            report.last_run_at = datetime.utcnow()
            await db.commit()

            return {
                "status": "success",
                "message": f"Report executed successfully and sent to {len(report.recipients)} recipient(s)",
                "execution_id": str(execution_id),
                "row_count": row_count,
                "sent_to": send_result['sent_to'],
                "files": {fmt: str(path) for fmt, path in generated_files.items()}
            }

        except Exception as e:
            # Unexpected error
            if execution_id:
                try:
                    result = await db.execute(
                        select(ReportExecution).where(ReportExecution.id == execution_id)
                    )
                    execution = result.scalar_one_or_none()
                    if execution:
                        execution.status = 'failed'
                        execution.error_message = f"Unexpected error: {str(e)}"
                        execution.execution_time_ms = int((time.time() - start_time) * 1000)
                        await db.commit()
                except:
                    pass

            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "scheduled_report_id": scheduled_report_id
            }


@shared_task(bind=True, name='app.tasks.reports.check_and_run_scheduled_reports')
def check_and_run_scheduled_reports(self):
    """
    Periodic task to check for scheduled reports that need to run.

    This task runs every 5 minutes via Celery Beat and:
    1. Finds all active reports with next_run_at <= now
    2. Spawns execution tasks for each
    3. Returns count of reports queued

    Returns:
        Dict with summary of queued reports
    """
    return asyncio.run(_check_and_queue_reports())


async def _check_and_queue_reports() -> Dict[str, Any]:
    """
    Async implementation of report checking and queuing.

    Returns:
        Dict with count of reports queued
    """
    async with AsyncSessionLocal() as db:
        try:
            schedule_service = ScheduleService()
            now = datetime.utcnow()

            # Find reports that should run
            result = await db.execute(
                select(ScheduledReport).where(
                    ScheduledReport.is_active == True,
                    ScheduledReport.next_run_at <= now
                )
            )
            reports_to_run = result.scalars().all()

            queued_count = 0
            queued_reports = []

            for report in reports_to_run:
                # Check if within tolerance window (5 minutes)
                if schedule_service.should_run_now(report.next_run_at, tolerance_minutes=5):
                    # Queue the execution task
                    run_scheduled_report_task.delay(str(report.id))
                    queued_count += 1
                    queued_reports.append({
                        "id": str(report.id),
                        "name": report.name,
                        "next_run_at": report.next_run_at.isoformat()
                    })

            return {
                "status": "success",
                "message": f"Queued {queued_count} report(s) for execution",
                "queued_count": queued_count,
                "reports": queued_reports,
                "checked_at": now.isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to check scheduled reports: {str(e)}",
                "queued_count": 0
            }
