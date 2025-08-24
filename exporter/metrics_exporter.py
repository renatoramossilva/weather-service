import exporter.exporter_services
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import requests
import bindl.logger


LOG = bindl.logger.setup_logger(__name__)


app_metrics = FastAPI()


@app_metrics.get("/")
def root():
    return {"message": "Metrics is running"}


@app_metrics.post("/observe")
def observe(metric_data: dict):
    """
    Sends a metric to the metrics exporter service.
    """
    if metric_data["type"] == "counter":
        exporter.exporter_services.counter(metric_data)


def post_metrics(metrics_data):
    try:
        LOG.info(f"Posting metrics data: {metrics_data}")
        requests.post("http://metrics-exporter:8082/observe", json=metrics_data)
    except Exception as e:
        LOG.error(f"Failed to send metric: {e}")


@app_metrics.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

