"""Celery consumer for processing messages from RabbitMQ."""

import json
import os

from celery import Celery
from dotenv import load_dotenv
import bindl.logger
import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh

LOG = bindl.logger.setup_logger(__name__)

# from app.services.redis import RABBITMQ_EXCHANGE, RABBITMQ_QUEUE, RABBITMQ_ROUTING_KEY

RABBITMQ_EXCHANGE = "weather_service_exchange"
# This should match the host name used in the docker-compose file
RABBITMQ_ROUTING_KEY = "mongodb_queue"
RABBITMQ_QUEUE = "weather_service_queue"

# Load environment variables from .env file
load_dotenv()

# Get RabbitMQ URL from environment variables
BROKER_URL = os.getenv("RABBITMQ_URL")
LOG.info(f"Using RabbitMQ broker URL: {BROKER_URL}")

# Celery configuration
app = Celery("weather_consumer", broker=BROKER_URL)

# Define the exchange and queue
# custom_exchange = Exchange(RABBITMQ_EXCHANGE, type="direct", durable=True)
# custom_queue = Queue(
#     RABBITMQ_QUEUE,
#     exchange=custom_exchange,
#     routing_key=RABBITMQ_ROUTING_KEY,
#     durable=True
# )


# # Register the queue with Celery
# app.conf.task_queues = (custom_queue,)
# app.conf.task_default_exchange = RABBITMQ_EXCHANGE
# app.conf.task_default_exchange_type = "direct"
# app.conf.task_default_routing_key = RABBITMQ_ROUTING_KEY
# app.conf.task_routes = {
#     'process_message': {
#         'queue': RABBITMQ_QUEUE,
#         'routing_key': RABBITMQ_ROUTING_KEY,
#     },
# }
@app.task
def process_message(message: dict) -> None:
    """
    Process a message from RabbitMQ.
    """
    LOG.info(f"Celery is processing message: {message}")
    try:
        redis_conn = rc.RedisConnectionHandler(host="redis").connect()
        if redis_conn.ping():
            redis_handler = rh.RedisHandler(redis_conn)
            redis_handler.set_value(
                message["cache_key"],
                json.dumps(message["payload"]),
                message["expire"],
            )
        else:
            LOG.error("Unable to connect to Redis.")
    except Exception as ex:
        LOG.error(f"Error saving on Redis: {ex}")
        return

    LOG.info(
        "Weather info saved on cache. This info will expire in %d minutes",
        message["expire"] / 60,
    )
