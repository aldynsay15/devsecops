from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import time
from app.routers import health_router, metrics_router, users_router, tasks_router
from app.dependencies import limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database import Base, engine
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API - DevSecOps Demo",
    description="""
    Демонстрационное приложение для показа работы CI/CD конвейера с интеграцией безопасности.
    
    ## Особенности демонстрации:
    - SQL Injection уязвимость (CWE-89)
    - Секреты в коде
    - Отключенные security headers (временно)
    
    Это демонстрационное приложение содержит намеренные уязвимости
    """,
    version="1.0.0",
    strict_content_type=False
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- УЯЗВИМОСТЬ: слишком широкие права CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", os.getenv("ALLOWED_HOSTS", "")],
)

# Prometheus метрики
instrumentator = Instrumentator(
    should_group_http_exceptions=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health", "/health/ready", "/health/live"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(users_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    """Корневой эндпоинт с информацией об API"""
    return {
        "message": "Task Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "metrics": "/metrics",
        "health": "/health"
    }
