from bindl.prometheus_wrapper.metrics_exporter import MetricsExporter

exporter = MetricsExporter()
exporter.register_counter(
    "requests_total", "Total number of requests", label_names=["method", "endpoint"]
)


def counter(metric_data):
    exporter.inc_counter(
        metric_data["name"],
        labels={"method": metric_data["method"], "endpoint": metric_data["endpoint"]},
    )
