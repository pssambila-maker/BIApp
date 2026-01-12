"""Celery tasks for scheduled reports."""
from celery import shared_task


@shared_task(bind=True, name='app.tasks.reports.check_and_run_scheduled_reports')
def check_and_run_scheduled_reports(self):
    """
    Periodic task to check for scheduled reports that need to run.

    This task runs every 5 minutes and finds all active scheduled reports
    where next_run_at <= now, then spawns individual tasks for each.
    """
    # TODO: Implement in Week 3
    # 1. Query ScheduledReport where is_active=True AND next_run_at <= now
    # 2. For each report: run_scheduled_report_task.delay(report_id)
    return "check_and_run_scheduled_reports: Not yet implemented"


@shared_task(bind=True, name='app.tasks.reports.run_scheduled_report_task')
def run_scheduled_report_task(self, scheduled_report_id: str):
    """
    Execute a specific scheduled report.

    Args:
        scheduled_report_id: UUID of the scheduled report to execute

    Steps:
        1. Load report configuration
        2. Execute query via ReportService
        3. Generate files in requested formats
        4. Send emails via EmailService
        5. Create ReportExecution record (status, files, sent_to)
        6. Update next_run_at using ScheduleService
    """
    # TODO: Implement in Week 3
    return f"run_scheduled_report_task({scheduled_report_id}): Not yet implemented"
