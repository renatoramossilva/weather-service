"""Set up a Redis connection and initialize a handler for interacting with it"""

import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh
import bindl.logger

import json


LOG = bindl.logger.setup_logger(__name__)
EXPIRE_TIME = 1800  # 30 minutes


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


async def get_info_from_redis(cache_key):
    LOG.info(f"Check if {cache_key} exists")
    try:
        LOG.info("Connecting")
        redis_client = get_redis_repo()
        LOG.info("Getting")
        cached_city = redis_client.get_value(cache_key)
    except Exception as ex:
        LOG.error(f"Error getting redis: {ex}")
        return None

    if cached_city:
        LOG.info("Getting city info (%r) from Redis cache", cache_key)
        return json.loads(cached_city)

    return None


async def save_info_redis(cache_key, result):
    try:
        redis_client = get_redis_repo()
        redis_client.set_value(cache_key, json.dumps(result), EXPIRE_TIME)
    except Exception as ex:
        LOG.erro(f"Error saving on Redis: {ex}")

    LOG.info("Saving info %s on Redis cache", result)
    LOG.info(
        "Weather info saved on cache. This info will expire in %d minutes",
        EXPIRE_TIME / 60,
    )
