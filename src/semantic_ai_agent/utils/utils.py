"""Shared Redis connection utilities."""

import redis as _redis


def ping_redis(url: str) -> bool:
    """Check whether Redis is reachable at the given URL.

    Args:
        url: The URL of the Redis server.

    Returns:
        True if the connection succeeds, False otherwise.
    """
    try:
        _redis.Redis.from_url(url).ping()
    except _redis.ConnectionError:
        return False
    return True


def try_connect_to_redis(url: str) -> _redis.Redis:
    """Connect to Redis or raise with a helpful message (used by notebooks).
    Returns:
        Redis client object if connection is successful.
    Raises:
        ConnectionError: If the connection to Redis fails.
    """
    client = ping_redis(url)
    if client is None:
        msg = f"Cannot connect to Redis at {url}"
        raise _redis.ConnectionError(msg)
    return client
