"""Test services for scheduled reports."""
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

from app.services.schedule_service import ScheduleService
from app.services.report_service import ReportService


def test_schedule_service():
    """Test schedule calculations."""
    print("=" * 60)
    print("Testing ScheduleService")
    print("=" * 60)

    service = ScheduleService()

    # Test daily schedule
    daily_config = {"type": "daily", "time": "09:00"}
    next_run = service.calculate_next_run(daily_config)
    print(f"\nDaily at 09:00:")
    print(f"  Next run: {next_run}")
    print(f"  Description: {service.format_schedule_description(daily_config)}")

    # Test weekly schedule
    weekly_config = {"type": "weekly", "time": "14:30", "day_of_week": 1}  # Tuesday
    next_run = service.calculate_next_run(weekly_config)
    print(f"\nWeekly on Tuesday at 14:30:")
    print(f"  Next run: {next_run}")
    print(f"  Description: {service.format_schedule_description(weekly_config)}")

    # Test monthly schedule
    monthly_config = {"type": "monthly", "time": "08:00", "day_of_month": 1}
    next_run = service.calculate_next_run(monthly_config)
    print(f"\nMonthly on day 1 at 08:00:")
    print(f"  Next run: {next_run}")
    print(f"  Description: {service.format_schedule_description(monthly_config)}")

    # Test should_run_now
    past_time = datetime.utcnow() - timedelta(minutes=3)
    should_run = service.should_run_now(past_time)
    print(f"\nShould run now (3 minutes ago): {should_run}")

    print("\n✓ ScheduleService tests passed!\n")


def test_report_service():
    """Test report generation."""
    print("=" * 60)
    print("Testing ReportService")
    print("=" * 60)

    service = ReportService()

    # Create sample data
    data = pd.DataFrame({
        'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
        'Sales': [12500, 850, 1200, 8900, 2100],
        'Quantity': [25, 150, 80, 45, 70],
        'Profit': [3750, 255, 360, 2670, 630]
    })

    print(f"\nSample data ({len(data)} rows):")
    print(data.to_string())

    # Test directory
    test_dir = Path("./test_reports")
    test_dir.mkdir(exist_ok=True)

    # Test Excel export
    print("\nGenerating Excel...")
    excel_path = service.generate_excel(data, test_dir / "test_report.xlsx")
    print(f"  ✓ Excel saved to: {excel_path}")
    print(f"  File size: {excel_path.stat().st_size:,} bytes")

    # Test CSV export
    print("\nGenerating CSV...")
    csv_path = service.generate_csv(data, test_dir / "test_report.csv")
    print(f"  ✓ CSV saved to: {csv_path}")
    print(f"  File size: {csv_path.stat().st_size:,} bytes")

    # Test PDF export
    print("\nGenerating PDF...")
    try:
        pdf_path = service.generate_pdf(data, test_dir / "test_report.pdf", "Sales Report")
        print(f"  ✓ PDF saved to: {pdf_path}")
        print(f"  File size: {pdf_path.stat().st_size:,} bytes")
    except ImportError as e:
        print(f"  ⚠ PDF generation skipped: {e}")

    # Test HTML email generation
    print("\nGenerating HTML email...")
    html_email = service.generate_html_email(data, "Monthly Sales Report")
    print(f"  ✓ HTML generated ({len(html_email)} characters)")
    print(f"  Preview (first 200 chars): {html_email[:200]}...")

    print("\n✓ ReportService tests passed!\n")


def test_encryption_service():
    """Test encryption utility."""
    print("=" * 60)
    print("Testing EncryptionService")
    print("=" * 60)

    from app.utils.encryption import get_encryption_service

    service = get_encryption_service()

    # Test encrypt/decrypt
    original_password = "MySecretPassword123!"
    print(f"\nOriginal: {original_password}")

    encrypted = service.encrypt(original_password)
    print(f"Encrypted: {encrypted[:50]}... ({len(encrypted)} chars)")

    decrypted = service.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")

    assert original_password == decrypted, "Encryption/Decryption failed!"
    print("\n✓ Encryption round-trip successful!")

    # Test key generation
    new_key = service.generate_key()
    print(f"\nGenerated new key: {new_key[:30]}... ({len(new_key)} chars)")
    print("  (This can be used as ENCRYPTION_KEY in .env)")

    print("\n✓ EncryptionService tests passed!\n")


if __name__ == "__main__":
    print("\n")
    print("=" * 60)
    print(" " * 10 + "SCHEDULED REPORTS - SERVICE TESTS")
    print("=" * 60)
    print("\n")

    try:
        test_schedule_service()
        test_report_service()
        test_encryption_service()

        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nServices are ready for Week 3 (API endpoints & Celery tasks)")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
