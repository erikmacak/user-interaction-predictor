from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from api.routes.predict import router as predict_router
from api.exception_handlers import (
    validation_exception_handler,
    domain_exception_handler,
)
from domain.errors import DomainError

app = FastAPI(
    title="User Interaction Predictor API",
    version="1.0.0",
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