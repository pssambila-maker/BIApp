"""Setup test data for Week 3 integration tests."""
import asyncio
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.semantic import SemanticEntity
from app.models.saved_query import SavedQuery


async def setup_test_saved_query():
    """Create a simple saved query for testing."""
    print("=" * 60)
    print("Setting up test data for Week 3 integration tests")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get test user
        print("\n[1] Loading test user...")
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            print("   [ERROR] No users found. Please create a user first.")
            return False

        print(f"   [OK] Using user: {user.email}")

        # Check for existing saved query
        print("\n[2] Checking for existing saved queries...")
        result = await db.execute(
            select(SavedQuery).where(SavedQuery.owner_id == user.id).limit(1)
        )
        existing_query = result.scalar_one_or_none()

        if existing_query:
            print(f"   [OK] Found existing saved query: {existing_query.name}")
            print(f"        ID: {existing_query.id}")
            return True

        # Get a semantic entity to use
        print("\n[3] Finding a semantic entity...")
        result = await db.execute(select(SemanticEntity).limit(1))
        entity = result.scalar_one_or_none()

        if not entity:
            print("   [ERROR] No semantic entities found. Please create an entity first.")
            return False

        print(f"   [OK] Using entity: {entity.name}")

        # Create test saved query
        print("\n[4] Creating test saved query...")
        saved_query = SavedQuery(
            owner_id=user.id,
            name="Test Sales Query",
            description="Test query for scheduled reports integration testing",
            entity_id=entity.id,
            query_config={
                "dimensions": [],
                "measures": [],
                "filters": []
            },
            is_favorite=False
        )
        db.add(saved_query)
        await db.commit()
        await db.refresh(saved_query)

        print(f"   [OK] Created saved query: {saved_query.name}")
        print(f"        ID: {saved_query.id}")

        print("\n" + "=" * 60)
        print("[SUCCESS] Test data setup complete!")
        print("=" * 60)
        print("\nYou can now run: python test_week3_integration.py")

        return True


if __name__ == "__main__":
    success = asyncio.run(setup_test_saved_query())
    sys.exit(0 if success else 1)
