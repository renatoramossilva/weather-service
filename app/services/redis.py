"""Set up a Redis connection and initialize a handler for interacting with it"""

from typing import Optional
import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh
import bindl.logger
import bindl.rabbitmq_wrapper.publisher as pub

import json


LOG = bindl.logger.setup_logger(__name__)
EXPIRE_TIME = 1800  # 30 minutes
# This should match the exchange name used in the RabbitMQ setup
RABBITMQ_EXCHANGE = "weather_service_exchange"
# This should match the host name used in the docker-compose file
RABBITMQ_HOST = "rabbitmq"


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


async def get_info_from_redis(cache_key: str) -> Optional[dict]:
    """Retrieve information from Redis cache.

    **Parameters**
        cache_key: The key under which the information is stored in Redis.
    **Returns**
        dict: The cached information if found, otherwise None.
    """
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


async def save_info_redis(cache_key: str, result: dict) -> None:
    """Publish a message to RabbitMQ to be processed by a worker to save the result in Redis.

    **Parameters**
        cache_key: The key under which the result will be stored in Redis.
        result: The result data to be saved in Redis.
    """
    LOG.info("Starting RabbitMQ publisher")
    # Initialize the RabbitMQ publisher
    rabbitmq_publisher = pub.RabbitmqPublisher(
        host=RABBITMQ_HOST, exchange=RABBITMQ_EXCHANGE
    )

    LOG.info("Publishing message to RabbitMQ exchange %s", RABBITMQ_EXCHANGE)
    # Post a message
    rabbitmq_publisher.send_message(
        dict(cache_key=cache_key, payload=result, expire=EXPIRE_TIME)
    )
