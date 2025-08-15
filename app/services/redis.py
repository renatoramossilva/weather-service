"""Set up a Redis connection and initialize a handler for interacting with it"""

import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh
import bindl.logger
from consumer.celery_consumer import process_message
import json


LOG = bindl.logger.setup_logger(__name__)
EXPIRATION_TIME = 1800  # 30 minutes

# This should match the exchange name used in the RabbitMQ setup
RABBITMQ_EXCHANGE = "weather_service_exchange"
# This should match the host name used in the docker-compose file
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_ROUTING_KEY = "mongodb_queue"
RABBITMQ_QUEUE = "weather_service_queue"


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


def save_info_redis(cache_key: str, result: dict) -> None:
    """Publish a message to RabbitMQ to be processed by a worker to save the result in Redis.

    **Parameters**
        cache_key: The key under which the city information will be stored in Redis.
        result: The city information to be cached, provided as a dictionary.
    """
    message = dict(cache_key=cache_key, payload=result, expire=EXPIRATION_TIME)
    LOG.debug("Publishing message to RabbitMQ... %s", message)
    try:
        process_message.delay(message)
    except Exception as e:
        LOG.error("Error publishing message to RabbitMQ: %s", e)
