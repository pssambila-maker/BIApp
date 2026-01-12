"""Test script to verify Celery worker configuration."""
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_celery_import():
    """Test that Celery app can be imported."""
    print("=" * 60)
    print("Testing Celery Worker Configuration")
    print("=" * 60)

    try:
        from app.celery_app import celery_app
        print("\n[OK] Celery app imported successfully")
        print(f"    Broker: {celery_app.conf.broker_url}")
        print(f"    Backend: {celery_app.conf.result_backend}")
        print(f"    Task modules: {celery_app.conf.include}")
    except Exception as e:
        print(f"\n[FAIL] Failed to import Celery app: {e}")
        return False

    return True


def test_task_imports():
    """Test that tasks can be imported."""
    print("\n" + "=" * 60)
    print("Testing Task Imports")
    print("=" * 60)

    try:
        from app.tasks.reports import run_scheduled_report_task, check_and_run_scheduled_reports
        print("\n[OK] Report tasks imported successfully")
        print(f"    - run_scheduled_report_task: {run_scheduled_report_task.name}")
        print(f"    - check_and_run_scheduled_reports: {check_and_run_scheduled_reports.name}")
    except Exception as e:
        print(f"\n[FAIL] Failed to import report tasks: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_beat_schedule():
    """Test Beat schedule configuration."""
    print("\n" + "=" * 60)
    print("Testing Celery Beat Schedule")
    print("=" * 60)

    try:
        from app.celery_app import celery_app
        schedule = celery_app.conf.beat_schedule

        print(f"\n[OK] Beat schedule configured with {len(schedule)} tasks:")
        for name, config in schedule.items():
            print(f"\n    Task: {name}")
            print(f"        Task name: {config['task']}")
            print(f"        Schedule: {config['schedule']}")
            if 'options' in config:
                print(f"        Options: {config['options']}")
    except Exception as e:
        print(f"\n[FAIL] Failed to check beat schedule: {e}")
        return False

    return True


def test_registered_tasks():
    """Test that tasks are registered with Celery."""
    print("\n" + "=" * 60)
    print("Testing Registered Tasks")
    print("=" * 60)

    try:
        from app.celery_app import celery_app

        # Force task discovery
        celery_app.autodiscover_tasks(['app.tasks'])

        registered = celery_app.tasks
        report_tasks = [name for name in registered.keys() if 'report' in name.lower()]

        print(f"\n[OK] Found {len(report_tasks)} report-related tasks:")
        for task_name in sorted(report_tasks):
            print(f"    - {task_name}")

        # Check for our specific tasks
        expected_tasks = [
            'app.tasks.reports.run_scheduled_report_task',
            'app.tasks.reports.check_and_run_scheduled_reports'
        ]

        for expected in expected_tasks:
            if expected in registered:
                print(f"\n    [OK] Task registered: {expected}")
            else:
                print(f"\n    [WARNING] Task not found: {expected}")
                print(f"              Available tasks: {list(registered.keys())[:5]}...")

    except Exception as e:
        print(f"\n[FAIL] Failed to check registered tasks: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Run all tests."""
    print("\n")
    print("#" * 60)
    print("# CELERY WORKER CONFIGURATION TEST")
    print("#" * 60)

    results = []

    # Test 1: Import Celery app
    results.append(("Celery App Import", test_celery_import()))

    # Test 2: Import tasks
    results.append(("Task Imports", test_task_imports()))

    # Test 3: Beat schedule
    results.append(("Beat Schedule", test_beat_schedule()))

    # Test 4: Registered tasks
    results.append(("Registered Tasks", test_registered_tasks()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nResults: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n[SUCCESS] All Celery worker tests passed!")
        print("\nNext steps:")
        print("1. Start Celery worker: celery -A app.celery_app worker --loglevel=info --pool=solo")
        print("2. Start Celery Beat: celery -A app.celery_app beat --loglevel=info")
        print("3. Monitor with Flower (optional): celery -A app.celery_app flower --port=5555")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Fix issues before starting worker.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
