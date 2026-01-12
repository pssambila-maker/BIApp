"""Celery application configuration for background tasks."""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery application
celery_app = Celery(
    "tableau_app",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.reports",
        "app.tasks.alerts",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={"master_name": "mymaster"},

    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Check for scheduled reports every 5 minutes
    'check-scheduled-reports': {
        'task': 'app.tasks.reports.check_and_run_scheduled_reports',
        'schedule': crontab(minute='*/5'),
        'options': {'expires': 300}  # Expire after 5 minutes
    },
    # Check for alerts every 5 minutes
    'check-alerts': {
        'task': 'app.tasks.alerts.check_and_evaluate_alerts',
        'schedule': crontab(minute='*/5'),
        'options': {'expires': 300}  # Expire after 5 minutes
    },
}


if __name__ == '__main__':
    celery_app.start()
