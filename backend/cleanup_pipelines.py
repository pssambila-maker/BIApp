"""
Cleanup script to delete all test transformation pipelines via API.
Usage: python cleanup_pipelines.py YOUR_ACCESS_TOKEN
"""
import sys
import requests

BASE_URL = "http://localhost:8000"


def cleanup_pipelines(access_token: str):
    """Delete all transformation pipelines for the authenticated user."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Get all pipelines
    print("Fetching all pipelines...")
    response = requests.get(f"{BASE_URL}/api/pipelines", headers=headers)

    if response.status_code != 200:
        print(f"Error fetching pipelines: {response.status_code}")
        print(response.text)
        return

    pipelines = response.json()

    if not pipelines:
        print("No pipelines found to delete.")
        return

    print(f"Found {len(pipelines)} pipeline(s) to delete.\n")

    # Delete each pipeline
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        pipeline_name = pipeline["name"]

        print(f"Deleting pipeline: {pipeline_name} ({pipeline_id})...")
        delete_response = requests.delete(
            f"{BASE_URL}/api/pipelines/{pipeline_id}",
            headers=headers
        )

        if delete_response.status_code == 204:
            print(f"✅ Successfully deleted: {pipeline_name}")
        else:
            print(f"❌ Failed to delete {pipeline_name}: {delete_response.status_code}")
            print(delete_response.text)
        print()

    print("Cleanup complete!")

    # Verify deletion
    verify_response = requests.get(f"{BASE_URL}/api/pipelines", headers=headers)
    remaining = verify_response.json()
    print(f"Remaining pipelines: {len(remaining)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cleanup_pipelines.py YOUR_ACCESS_TOKEN")
        print("\nGet your access token by:")
        print("1. POST /api/auth/login with your credentials")
        print("2. Copy the 'access_token' from the response")
        sys.exit(1)

    token = sys.argv[1]
    cleanup_pipelines(token)
