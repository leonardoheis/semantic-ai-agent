"""Shared Redis connection utilities."""

import redis as _redis


def ping_redis(url: str) -> _redis.Redis | None:
    """Connect to Redis and return the client, or None on any failure."""
    try:
        client = _redis.Redis.from_url(url)
        client.ping()
        return client
    except Exception:
        return None


def try_connect_to_redis(url: str) -> _redis.Redis:
    """Connect to Redis or raise with a helpful message (used by notebooks)."""
    client = ping_redis(url)
    if client is None:
        print(
            "Cannot connect to Redis. "
            "Try: docker run -d --name redis -p 6379:6379 redis/redis-stack:latest"
        )
        raise _redis.ConnectionError(f"Cannot connect to Redis at {url}")
    print("Redis is running and accessible!")
    return client
