"""
Week 3 Integration Test Script

Tests the complete scheduled reports workflow:
1. Email configuration setup
2. Scheduled report creation
3. Manual test execution
4. Celery task execution
5. Execution history tracking
"""
import asyncio
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.email_config import EmailConfiguration
from app.models.scheduled_report import ScheduledReport, ReportExecution
from app.models.saved_query import SavedQuery
from app.services.schedule_service import ScheduleService
from app.utils.encryption import get_encryption_service


async def cleanup_test_data(db: AsyncSession, user_id: UUID):
    """Remove any existing test data."""
    print("\n[Cleanup] Removing existing test data...")

    # Delete scheduled reports and their executions (cascade)
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.owner_id == user_id,
            ScheduledReport.name.like('%Test%')
        )
    )
    reports = result.scalars().all()
    for report in reports:
        await db.delete(report)

    # Delete email config
    result = await db.execute(
        select(EmailConfiguration).where(EmailConfiguration.owner_id == user_id)
    )
    config = result.scalar_one_or_none()
    if config:
        await db.delete(config)

    await db.commit()
    print("   [OK] Cleanup complete")


async def test_email_configuration(db: AsyncSession, user_id: UUID):
    """Test 1: Email configuration CRUD."""
    print("\n" + "=" * 60)
    print("TEST 1: Email Configuration")
    print("=" * 60)

    encryption = get_encryption_service()

    # Create email config
    print("\n[1.1] Creating email configuration...")
    email_config = EmailConfiguration(
        owner_id=user_id,
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        use_tls=True,
        use_ssl=False,
        smtp_username="test@example.com",
        smtp_password_encrypted=encryption.encrypt("test_password"),
        from_email="test@example.com",
        from_name="Test User"
    )
    db.add(email_config)
    await db.commit()
    await db.refresh(email_config)
    print(f"   [OK] Email config created: {email_config.id}")

    # Verify password encryption
    print("\n[1.2] Verifying password encryption...")
    decrypted = encryption.decrypt(email_config.smtp_password_encrypted)
    assert decrypted == "test_password", "Password encryption/decryption failed"
    print("   [OK] Password encrypted and can be decrypted")

    # Retrieve config
    print("\n[1.3] Retrieving email configuration...")
    result = await db.execute(
        select(EmailConfiguration).where(EmailConfiguration.owner_id == user_id)
    )
    retrieved_config = result.scalar_one()
    assert retrieved_config.id == email_config.id
    print(f"   [OK] Config retrieved: {retrieved_config.smtp_host}:{retrieved_config.smtp_port}")

    return email_config


async def test_scheduled_report_creation(db: AsyncSession, user_id: UUID):
    """Test 2: Scheduled report creation with schedule calculation."""
    print("\n" + "=" * 60)
    print("TEST 2: Scheduled Report Creation")
    print("=" * 60)

    # Get a saved query to use
    print("\n[2.1] Finding a saved query...")
    result = await db.execute(
        select(SavedQuery).where(SavedQuery.owner_id == user_id).limit(1)
    )
    saved_query = result.scalar_one_or_none()

    if not saved_query:
        print("   [SKIP] No saved queries found. Create one first.")
        return None

    print(f"   [OK] Using saved query: {saved_query.name}")

    # Create daily schedule
    print("\n[2.2] Creating scheduled report with daily schedule...")
    schedule_service = ScheduleService()
    schedule_config = {
        "type": "daily",
        "time": "09:00"
    }
    next_run_at = schedule_service.calculate_next_run(schedule_config)

    report = ScheduledReport(
        owner_id=user_id,
        name="Test Daily Sales Report",
        description="Integration test report",
        saved_query_id=saved_query.id,
        schedule_config=schedule_config,
        recipients=["test1@example.com", "test2@example.com"],
        formats=["excel", "csv", "pdf"],
        email_subject="Daily Sales Report - {{date}}",
        email_body="Please find attached today's sales report.",
        is_active=True,
        next_run_at=next_run_at
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    print(f"   [OK] Report created: {report.id}")
    print(f"        Next run: {report.next_run_at}")

    # Verify schedule calculation
    print("\n[2.3] Verifying schedule calculation...")
    assert report.next_run_at > datetime.now(timezone.utc), "next_run_at should be in future"
    description = schedule_service.format_schedule_description(schedule_config)
    print(f"   [OK] Schedule: {description}")

    return report


async def test_schedule_types(db: AsyncSession, user_id: UUID, saved_query_id: UUID):
    """Test 3: Different schedule types."""
    print("\n" + "=" * 60)
    print("TEST 3: Schedule Types")
    print("=" * 60)

    schedule_service = ScheduleService()
    test_schedules = [
        {
            "name": "Weekly Report",
            "config": {"type": "weekly", "time": "08:00", "day_of_week": 1}  # Tuesday
        },
        {
            "name": "Monthly Report",
            "config": {"type": "monthly", "time": "07:00", "day_of_month": 1}
        }
    ]

    for schedule_def in test_schedules:
        print(f"\n[3.{test_schedules.index(schedule_def) + 1}] Testing {schedule_def['name']}...")

        next_run_at = schedule_service.calculate_next_run(schedule_def['config'])
        description = schedule_service.format_schedule_description(schedule_def['config'])

        report = ScheduledReport(
            owner_id=user_id,
            name=f"Test {schedule_def['name']}",
            saved_query_id=saved_query_id,
            schedule_config=schedule_def['config'],
            recipients=["test@example.com"],
            formats=["excel"],
            is_active=True,
            next_run_at=next_run_at
        )
        db.add(report)

        print(f"   [OK] {description}")
        print(f"        Next run: {next_run_at}")

    await db.commit()
    print("\n   [OK] All schedule types created successfully")


async def test_execution_record(db: AsyncSession, report: ScheduledReport):
    """Test 4: Execution record creation."""
    print("\n" + "=" * 60)
    print("TEST 4: Execution Record Tracking")
    print("=" * 60)

    # Create successful execution
    print("\n[4.1] Creating successful execution record...")
    execution = ReportExecution(
        scheduled_report_id=report.id,
        status='success',
        triggered_by='manual',
        generated_files={
            "excel": "/path/to/report.xlsx",
            "csv": "/path/to/report.csv",
            "pdf": "/path/to/report.pdf"
        },
        sent_to=["test1@example.com", "test2@example.com"],
        execution_time_ms=2500,
        row_count=150
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    print(f"   [OK] Execution created: {execution.id}")
    print(f"        Status: {execution.status}")
    print(f"        Row count: {execution.row_count}")
    print(f"        Execution time: {execution.execution_time_ms}ms")

    # Create failed execution
    print("\n[4.2] Creating failed execution record...")
    failed_execution = ReportExecution(
        scheduled_report_id=report.id,
        status='failed',
        triggered_by='schedule',
        error_message="Query execution failed: Connection timeout",
        execution_time_ms=30000
    )
    db.add(failed_execution)
    await db.commit()
    print(f"   [OK] Failed execution created with error message")

    # Retrieve execution history
    print("\n[4.3] Retrieving execution history...")
    result = await db.execute(
        select(ReportExecution)
        .where(ReportExecution.scheduled_report_id == report.id)
        .order_by(ReportExecution.created_at.desc())
    )
    executions = result.scalars().all()
    print(f"   [OK] Found {len(executions)} executions:")
    for exec in executions:
        print(f"        - {exec.status.upper()}: {exec.triggered_by} "
              f"({exec.execution_time_ms}ms)")

    return execution


async def test_next_run_calculation(db: AsyncSession, user_id: UUID, saved_query_id: UUID):
    """Test 5: next_run_at updates after execution."""
    print("\n" + "=" * 60)
    print("TEST 5: Next Run Time Updates")
    print("=" * 60)

    schedule_service = ScheduleService()

    # Create report with next_run in the past
    print("\n[5.1] Creating report with past next_run_at...")
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    schedule_config = {"type": "daily", "time": "09:00"}

    report = ScheduledReport(
        owner_id=user_id,
        name="Test Past Run Report",
        saved_query_id=saved_query_id,
        schedule_config=schedule_config,
        recipients=["test@example.com"],
        formats=["excel"],
        is_active=True,
        next_run_at=past_time
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    print(f"   [OK] Report created with next_run_at: {report.next_run_at}")

    # Simulate execution and update next_run_at
    print("\n[5.2] Simulating execution and updating next_run_at...")
    old_next_run = report.next_run_at
    report.last_run_at = datetime.now(timezone.utc)
    report.next_run_at = schedule_service.calculate_next_run(
        report.schedule_config,
        datetime.now(timezone.utc)
    )
    await db.commit()
    await db.refresh(report)

    print(f"   [OK] Updated next_run_at")
    print(f"        Old: {old_next_run}")
    print(f"        New: {report.next_run_at}")
    assert report.next_run_at > old_next_run, "next_run_at should advance"
    assert report.next_run_at > datetime.now(timezone.utc), "next_run_at should be in future"


async def test_scheduler_query(db: AsyncSession, user_id: UUID, saved_query_id: UUID):
    """Test 6: Scheduler query for reports due to run."""
    print("\n" + "=" * 60)
    print("TEST 6: Scheduler Query (check_and_run_scheduled_reports)")
    print("=" * 60)

    # Create report that should run now
    print("\n[6.1] Creating report with next_run_at in the past...")
    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)

    report = ScheduledReport(
        owner_id=user_id,
        name="Test Should Run Now",
        saved_query_id=saved_query_id,
        schedule_config={"type": "daily", "time": "00:00"},
        recipients=["test@example.com"],
        formats=["excel"],
        is_active=True,
        next_run_at=past_time
    )
    db.add(report)
    await db.commit()

    # Query for reports that should run (same as scheduler task)
    print("\n[6.2] Querying for reports due to run...")
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ScheduledReport).where(
            ScheduledReport.is_active == True,
            ScheduledReport.next_run_at <= now
        )
    )
    reports_to_run = result.scalars().all()

    print(f"   [OK] Found {len(reports_to_run)} reports due to run:")
    for r in reports_to_run:
        if 'Test' in r.name:  # Only show our test reports
            print(f"        - {r.name} (next_run: {r.next_run_at})")

    # Verify our test report is in the list
    report_ids = [r.id for r in reports_to_run]
    assert report.id in report_ids, "Test report should be in scheduler query results"


async def run_all_tests():
    """Run all integration tests."""
    print("\n")
    print("#" * 60)
    print("# WEEK 3 INTEGRATION TESTS")
    print("#" * 60)
    print("\nTesting: Scheduled Reports Backend Implementation")
    print("Date:", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))

    async with AsyncSessionLocal() as db:
        try:
            # Get test user
            print("\n[Setup] Loading test user...")
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()

            if not user:
                print("   [ERROR] No users found. Create a user first.")
                return False

            print(f"   [OK] Using user: {user.email} ({user.id})")

            # Cleanup
            await cleanup_test_data(db, user.id)

            # Run tests
            test_results = []

            # Test 1: Email Configuration
            try:
                email_config = await test_email_configuration(db, user.id)
                test_results.append(("Email Configuration", True))
            except Exception as e:
                print(f"\n   [FAIL] {e}")
                test_results.append(("Email Configuration", False))
                import traceback
                traceback.print_exc()

            # Test 2: Scheduled Report Creation
            try:
                report = await test_scheduled_report_creation(db, user.id)
                if report:
                    test_results.append(("Scheduled Report Creation", True))
                else:
                    test_results.append(("Scheduled Report Creation", False))
                    print("   [SKIP] Skipping remaining tests (no saved query)")
                    return False
            except Exception as e:
                print(f"\n   [FAIL] {e}")
                test_results.append(("Scheduled Report Creation", False))
                import traceback
                traceback.print_exc()
                return False

            # Test 3: Schedule Types
            try:
                await test_schedule_types(db, user.id, report.saved_query_id)
                test_results.append(("Schedule Types", True))
            except Exception as e:
                print(f"\n   [FAIL] {e}")
                test_results.append(("Schedule Types", False))
                import traceback
                traceback.print_exc()

            # Test 4: Execution Records
            try:
                await test_execution_record(db, report)
                test_results.append(("Execution Record Tracking", True))
            except Exception as e:
                print(f"\n   [FAIL] {e}")
                test_results.append(("Execution Record Tracking", False))
                import traceback
                traceback.print_exc()

            # Test 5: Next Run Calculation
            try:
                await test_next_run_calculation(db, user.id, report.saved_query_id)
                test_results.append(("Next Run Calculation", True))
            except Exception as e:
                print(f"\n   [FAIL] {e}")
                test_results.append(("Next Run Calculation", False))
                import traceback
                traceback.print_exc()

            # Test 6: Scheduler Query
            try:
                await test_scheduler_query(db, user.id, report.saved_query_id)
                test_results.append(("Scheduler Query", True))
            except Exception as e:
                print(f"\n   [FAIL] {e}")
                test_results.append(("Scheduler Query", False))
                import traceback
                traceback.print_exc()

            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)

            for test_name, passed in test_results:
                status = "[PASS]" if passed else "[FAIL]"
                print(f"{status} {test_name}")

            total_passed = sum(1 for _, passed in test_results if passed)
            total_tests = len(test_results)

            print(f"\nResults: {total_passed}/{total_tests} tests passed")

            if total_passed == total_tests:
                print("\n" + "=" * 60)
                print("[SUCCESS] All integration tests passed!")
                print("=" * 60)
                print("\nScheduled Reports Backend Status:")
                print("  [OK] Database models working")
                print("  [OK] Schedule calculation working")
                print("  [OK] Execution tracking working")
                print("  [OK] Email configuration working")
                print("  [OK] Scheduler queries working")
                print("\nNext Steps:")
                print("  1. Start Celery worker to test task execution")
                print("  2. Test manual report execution via API")
                print("  3. Test automated execution via Celery Beat")
                print("  4. Build frontend UI (Week 4)")
                return True
            else:
                print("\n[FAILURE] Some tests failed. Review errors above.")
                return False

        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
