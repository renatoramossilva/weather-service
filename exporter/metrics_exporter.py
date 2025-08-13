import exporter.exporter_services
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import requests


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
        requests.post("http://metrics-exporter:8082/observe", json=metrics_data)
    except Exception as e:
        print.error(f"Failed to send metric: {e}")


@app_metrics.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
