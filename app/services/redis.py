"""Set up a Redis connection and initialize a handler for interacting with it"""

import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh
import bindl.logger

import json


LOG = bindl.logger.setup_logger(__name__)
EXPIRATION_TIME = 1800  # 30 minutes


class RedisConnectionError(Exception):
    pass


def get_redis_repo() -> rc.RedisConnectionHandler:
    """Connect to a Redis server.

    This function establishes a connection to a Redis server using the RedisConnectionHandler.
    It verifies the connection by sending a ping request. If the connection is successful,
    a log message is recorded indicating that Redis is connected. Otherwise, an error
    message is logged. Finally, it returns a RedisHandler instance initialized with the
    established connection.

    **Returns**
        RedisHandler: An instance of RedisHandler initialized with the Redis connection.
    **Raises**
        Exception: If the Redis connection cannot be established.
    """
    redis_conn = rc.RedisConnectionHandler(host="redis").connect()
    if redis_conn.ping():
        return rh.RedisHandler(redis_conn)
    else:
        LOG.error("Unable to connect to Redis.")


async def get_info_from_redis(cache_key: str) -> dict | None:
    """Retrieve cached city information from Redis.

    This function checks if a city information cache exists in Redis using the provided cache key.
    If the cache exists, it retrieves the cached data, logs the retrieval, and returns the
    cached city information as a dictionary. If the cache does not exist, it logs the cache miss
    and returns None.

    **Parameters**
        cache_key: The key used to access the cached city information in Redis.

    **Returns**
        The cached city information as a dictionary if it exists, otherwise None.
    """
    LOG.info(f"Check if {cache_key} exists on Redis cache")

    try:
        redis_client = get_redis_repo()
        cached_city = redis_client.get_value(cache_key)
    except Exception as ex:
        LOG.error(f"Error : {ex}")

    if cached_city:
        LOG.info("Getting city info (%r) from Redis cache", cache_key)
        return json.loads(cached_city)

    LOG.info("City info not found on Redis cache: %s", cache_key)
    return None


async def save_info_redis(cache_key: str, result: dict) -> None:
    """Save city information to Redis cache.

    This function saves the provided city information to Redis cache using the specified cache key.
    It serializes the city information to JSON format and sets it in Redis

    **Parameters**
        cache_key: The key under which the city information will be stored in Redis.
        result: The city information to be cached, provided as a dictionary.
    """
    LOG.info("Saving info %s on Redis cache", result)

    try:
        redis_client = get_redis_repo()
        redis_client.set_value(cache_key, json.dumps(result), EXPIRATION_TIME)
    except Exception as ex:
        LOG.error(f"Error saving on Redis: {ex}")
        return

    LOG.info(
        "Weather info saved on cache. This info will expire in %d minutes",
        EXPIRATION_TIME / 60,
    )
