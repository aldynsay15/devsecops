from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(
        status_code=429,
        detail="Too many requests. Please try again later."
    )
