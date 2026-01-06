"""Initialize database with schema and seed data."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.db.session import init_db, AsyncSessionLocal
from app.models.user import User, Role
from app.utils.security import get_password_hash


async def create_default_roles():
    """Create default roles."""
    async with AsyncSessionLocal() as db:
        # Admin role
        admin_role = Role(
            name="admin",
            description="Administrator with full access",
            permissions={
                "dashboards": ["read", "write", "delete", "publish"],
                "data_sources": ["read", "write", "delete"],
                "semantic_models": ["read", "write", "delete"],
                "users": ["read", "write", "delete"]
            }
        )
        db.add(admin_role)

        # Editor role
        editor_role = Role(
            name="editor",
            description="Can create and edit content",
            permissions={
                "dashboards": ["read", "write", "publish"],
                "data_sources": ["read", "write"],
                "semantic_models": ["read", "write"]
            }
        )
        db.add(editor_role)

        # Viewer role
        viewer_role = Role(
            name="viewer",
            description="Read-only access",
            permissions={
                "dashboards": ["read"],
                "data_sources": ["read"],
                "semantic_models": ["read"]
            }
        )
        db.add(viewer_role)

        await db.commit()
        print("✓ Created default roles: admin, editor, viewer")


async def create_admin_user():
    """Create default admin user."""
    async with AsyncSessionLocal() as db:
        admin_user = User(
            username="admin",
            email="admin@tableauapp.local",
            full_name="System Administrator",
            password_hash=get_password_hash("admin123"),  # Change this!
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        await db.commit()
        print("✓ Created admin user (username: admin, password: admin123)")
        print("  ⚠ IMPORTANT: Change the admin password after first login!")


async def main():
    """Main initialization function."""
    print("Initializing Tableau App database...")
    print()

    try:
        # Create tables
        print("Creating database tables...")
        await init_db()
        print("✓ Database tables created")
        print()

        # Create default roles
        print("Creating default roles...")
        await create_default_roles()
        print()

        # Create admin user
        print("Creating admin user...")
        await create_admin_user()
        print()

        print("=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the backend server: cd backend && python -m app.main")
        print("2. Open http://localhost:8000/docs to test the API")
        print("3. Login with username 'admin' and password 'admin123'")
        print("4. Change the admin password immediately!")
        print()

    except Exception as e:
        print(f"✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
