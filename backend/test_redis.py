"""Test Redis connection for Celery broker."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_redis_connection():
    """Test connection to Redis broker."""
    print("=" * 60)
    print("Testing Redis Connection")
    print("=" * 60)

    try:
        import redis
        from app.config import settings

        # Parse Redis URL
        broker_url = settings.celery_broker_url
        print(f"\nBroker URL: {broker_url}")

        # Connect to Redis
        r = redis.from_url(broker_url)
        response = r.ping()

        if response:
            print("\n[OK] Redis is running and accessible")
            print(f"    Response: {response}")

            # Get Redis info
            info = r.info('server')
            print(f"\n    Redis Version: {info.get('redis_version', 'unknown')}")
            print(f"    Redis Mode: {info.get('redis_mode', 'unknown')}")
            print(f"    Uptime: {info.get('uptime_in_seconds', 0)} seconds")

            return True
        else:
            print("\n[FAIL] Redis ping returned False")
            return False

    except redis.ConnectionError as e:
        print(f"\n[FAIL] Could not connect to Redis: {e}")
        print("\nTo start Redis:")
        print("  - Windows: Start Redis service or run redis-server.exe")
        print("  - Linux/Mac: sudo service redis-server start")
        print("  - Docker: docker run -d -p 6379:6379 redis:latest")
        return False
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_redis_connection()
    sys.exit(0 if success else 1)
