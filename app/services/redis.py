"""Set up a Redis connection and initialize a handler for interacting with it"""

import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh


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
        print("Unable to connect to Redis.")
