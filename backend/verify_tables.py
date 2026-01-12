"""Verify new tables exist in database."""
import asyncio
from sqlalchemy import text
from app.db.session import engine


async def verify_tables():
    """Check if new tables were created."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename IN (
                    'scheduled_reports',
                    'report_executions',
                    'alerts',
                    'alert_executions',
                    'email_configurations'
                )
                ORDER BY tablename
            """)
        )
        tables = [row[0] for row in result]
        print("Found tables:")
        for table in tables:
            print(f"  - {table}")

        expected = ['alert_executions', 'alerts', 'email_configurations', 'report_executions', 'scheduled_reports']
        if set(tables) == set(expected):
            print("\n✓ All tables created successfully!")
        else:
            missing = set(expected) - set(tables)
            if missing:
                print(f"\n✗ Missing tables: {missing}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_tables())
