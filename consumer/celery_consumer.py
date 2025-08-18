"""Celery consumer for processing messages from RabbitMQ."""

import json
import os

from celery import Celery
from dotenv import load_dotenv
from kombu import Exchange, Queue
import bindl.logger
import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh

LOG = bindl.logger.setup_logger(__name__)

RABBITMQ_EXCHANGE = "weather_service_exchange"

# This queue name should match the one used in the Dockerfile.worker
RABBITMQ_REDIS_CACHE_QUEUE = "redis_cache_queue"
RABBITMQ_REDIS_CACHE_ROUTING_KEY = "redis_cache_routing_key"

# Load environment variables from .env file
load_dotenv()

# Get RabbitMQ URL from environment variables
BROKER_URL = os.getenv("RABBITMQ_URL")
LOG.info(f"Using RabbitMQ broker URL: {BROKER_URL}")

# Celery configuration
app = Celery("celery_app", broker=BROKER_URL, backend="rpc://")

cache_exchange = Exchange(RABBITMQ_EXCHANGE, type="direct")

task_queues = (
    Queue(
        RABBITMQ_REDIS_CACHE_QUEUE,
        exchange=cache_exchange,
        routing_key=RABBITMQ_REDIS_CACHE_ROUTING_KEY,
        durable=True,
    ),
)

task_routes = {
    "app.tasks.process_message": {
        "queue": RABBITMQ_REDIS_CACHE_QUEUE,
        "routing_key": RABBITMQ_REDIS_CACHE_ROUTING_KEY,
    },
}

app.conf.update(
    task_default_queue=RABBITMQ_REDIS_CACHE_QUEUE,
    task_default_exchange=RABBITMQ_EXCHANGE,
    task_default_routing_key=RABBITMQ_REDIS_CACHE_ROUTING_KEY,
    task_queues=task_queues,
    task_routes=task_routes,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_transport_options={"confirm_publish": True},
    task_ignore_result=True,
)


@app.task(name="app.tasks.process_message")
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
