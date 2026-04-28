"""Prometheus-метрики воркера (multiprocess-совместимые)."""

from __future__ import annotations

import os

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    multiprocess,
    start_http_server,
)

from app.config import settings

scans_total = Counter(
    "mdmscan_scans_total",
    "Total image scans completed",
    ["status"],  # "done" | "failed"
)

findings_total = Counter(
    "mdmscan_findings_total",
    "Total findings across all scans",
    ["category", "severity"],
)

scanner_duration_seconds = Histogram(
    "mdmscan_scanner_duration_seconds",
    "Duration of individual scanner runs",
    ["scanner", "status"],
    buckets=[5, 10, 30, 60, 120, 300, 600],
)

scan_duration_seconds = Histogram(
    "mdmscan_scan_duration_seconds",
    "Total duration of a full scan",
    ["status"],
    buckets=[10, 30, 60, 120, 300, 600, 1800],
)

cleanup_runs_total = Counter(
    "mdmscan_cleanup_runs_total",
    "Periodic cleanup task executions",
    ["task", "status"],
)


def start_metrics_server() -> None:
    """Start aggregated metrics HTTP server (reads from prometheus_multiproc_dir)."""
    os.makedirs(settings.prometheus_multiproc_dir, exist_ok=True)
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    start_http_server(settings.metrics_port, registry=registry)
