"""Celery tasks for alerts."""
from celery import shared_task


@shared_task(bind=True, name='app.tasks.alerts.check_and_evaluate_alerts')
def check_and_evaluate_alerts(self):
    """
    Periodic task to check for alerts that need evaluation.

    This task runs every 5 minutes and finds all active alerts that
    should be checked based on their check_frequency.
    """
    # TODO: Implement in Week 5-6
    # 1. Query Alert where is_active=True AND should check based on check_frequency
    # 2. For each alert: evaluate_alert_task.delay(alert_id)
    return "check_and_evaluate_alerts: Not yet implemented"


@shared_task(bind=True, name='app.tasks.alerts.evaluate_alert_task')
def evaluate_alert_task(self, alert_id: str):
    """
    Evaluate a specific alert condition.

    Args:
        alert_id: UUID of the alert to evaluate

    Steps:
        1. Execute alert query
        2. Evaluate condition based on alert_type
        3. If triggered: send notification
        4. Create AlertExecution record
    """
    # TODO: Implement in Week 5-6
    return f"evaluate_alert_task({alert_id}): Not yet implemented"
