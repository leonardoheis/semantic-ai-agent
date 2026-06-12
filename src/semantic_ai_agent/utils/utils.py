"""Shared Redis connection utilities."""

import redis as _redis


def ping_redis(url: str) -> _redis.Redis | None:
    """Connect to Redis and return the client, or None on any failure.
    Returns:
        Redis client object if connection is successful, otherwise None.
    """
    try:
        client = _redis.Redis.from_url(url)
        client.ping()
        return client
    except Exception:
        return None


def try_connect_to_redis(url: str) -> _redis.Redis:
    """Connect to Redis or raise with a helpful message (used by notebooks).
    Returns:
        Redis client object if connection is successful.
    """
    client = ping_redis(url)
    if client is None:
        msg = f"Cannot connect to Redis at {url}"
        raise _redis.ConnectionError(msg)
    return client
