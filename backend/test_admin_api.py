"""Test script for admin user management API endpoints."""
import asyncio
import httpx
from pprint import pprint

BASE_URL = "http://localhost:8000/api"

async def test_admin_endpoints():
    """Test all admin user management endpoints."""

    async with httpx.AsyncClient() as client:
        # Step 1: Login as superuser
        print("\n" + "="*70)
        print("STEP 1: Login as Superuser")
        print("="*70)

        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": "testuser",
                "password": "password123"  # Update with actual password
            }
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful!")
        print(f"Token: {token[:50]}...")

        # Step 2: List all users
        print("\n" + "="*70)
        print("STEP 2: List All Users")
        print("="*70)

        users_response = await client.get(
            f"{BASE_URL}/users",
            headers=headers
        )

        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"✅ Found {users_data['total']} users:")
            for user in users_data['users']:
                print(f"\n  • {user['username']} ({user['email']})")
                print(f"    ID: {user['id']}")
                print(f"    Active: {user['is_active']}")
                print(f"    Superuser: {user['is_superuser']}")
        else:
            print(f"❌ Failed to list users: {users_response.status_code}")
            print(users_response.text)

        # Step 3: Get specific user
        print("\n" + "="*70)
        print("STEP 3: Get Specific User")
        print("="*70)

        if users_response.status_code == 200:
            first_user_id = users_data['users'][0]['id']
            user_response = await client.get(
                f"{BASE_URL}/users/{first_user_id}",
                headers=headers
            )

            if user_response.status_code == 200:
                user = user_response.json()
                print(f"✅ User details:")
                pprint(user)
            else:
                print(f"❌ Failed: {user_response.status_code}")

        # Step 4: Filter users
        print("\n" + "="*70)
        print("STEP 4: Filter Active Users")
        print("="*70)

        active_response = await client.get(
            f"{BASE_URL}/users?is_active=true",
            headers=headers
        )

        if active_response.status_code == 200:
            active_data = active_response.json()
            print(f"✅ Found {active_data['total']} active users")
        else:
            print(f"❌ Failed: {active_response.status_code}")

        print("\n" + "="*70)
        print("STEP 5: Filter Superusers")
        print("="*70)

        super_response = await client.get(
            f"{BASE_URL}/users?is_superuser=true",
            headers=headers
        )

        if super_response.status_code == 200:
            super_data = super_response.json()
            print(f"✅ Found {super_data['total']} superusers")
            for user in super_data['users']:
                print(f"  • {user['username']}")
        else:
            print(f"❌ Failed: {super_response.status_code}")

        print("\n" + "="*70)
        print("✅ All tests completed!")
        print("="*70)
        print("\nAvailable Admin Endpoints:")
        print("  GET    /api/users - List all users")
        print("  GET    /api/users/{id} - Get user details")
        print("  PUT    /api/users/{id} - Update user")
        print("  DELETE /api/users/{id} - Delete user")
        print("  POST   /api/users/{id}/reset-password - Reset password")
        print("  POST   /api/users/{id}/promote-superuser - Promote to superuser")
        print("  POST   /api/users/{id}/demote-superuser - Demote from superuser")
        print("  POST   /api/users/{id}/activate - Activate user")
        print("  POST   /api/users/{id}/deactivate - Deactivate user")

if __name__ == "__main__":
    asyncio.run(test_admin_endpoints())
