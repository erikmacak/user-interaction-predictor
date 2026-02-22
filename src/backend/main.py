from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.settings import settings
from services.predictor.registry import PredictorRegistry
from api.routes.predict import router as predict_router
from api.routes.auth import router as auth_router
from api.exception_handlers import (
    validation_exception_handler,
    domain_exception_handler,
)
from domain.errors import DomainError, UnsupportedPredictorVersionError

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        PredictorRegistry.get(settings.PREDICTOR_VERSION)
        print("✅ Predictor registry initialized")
    except UnsupportedPredictorVersionError as exc:
        raise RuntimeError(f"Application startup failed: {exc}")
    
    yield
    
    print("👋 Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True, 
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Cookie"],
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    DomainError,
    domain_exception_handler,
)

auth_router_with_limits = auth_router
auth_router_with_limits.routes[0].endpoint = limiter.limit("5/minute")(
    auth_router_with_limits.routes[0].endpoint
)

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["authentication"],
)

app.include_router(
    predict_router,
    prefix="/api",
    tags=["prediction"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }