from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from core.settings import settings
from services.predictor.registry import PredictorRegistry
from api.routes.predict import router as predict_router
from api.exception_handlers import (
    validation_exception_handler,
    domain_exception_handler,
)
from domain.errors import DomainError, UnsupportedPredictorVersionError

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        PredictorRegistry.get(settings.PREDICTOR_VERSION)
    except UnsupportedPredictorVersionError as exc:
        raise RuntimeError(
            f"Application startup failed: {exc}"
        )

    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    DomainError,
    domain_exception_handler,
)

app.include_router(
    predict_router,
    prefix="/api",
    tags=["prediction"],
)