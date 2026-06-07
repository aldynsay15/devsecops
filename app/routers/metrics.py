from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge
import psutil
import os

router = APIRouter(tags=["metrics"])

# Пользовательские метрики для демонстрации
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('active_users_total', 'Total active users')

@router.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint.
    Интеграция с Prometheus для мониторинга.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/metrics/system")
async def system_metrics():
    """
    Системные метрики для демонстрации возможностей мониторинга
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
    }
