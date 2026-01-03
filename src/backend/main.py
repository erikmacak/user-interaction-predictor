from fastapi import FastAPI
from api.routes.predict import router as predict_router

app = FastAPI(
    title="User Interaction Predictor API",
    version="1.0.0",
)

app.include_router(
    predict_router,
    prefix="/api",
    tags=["prediction"],
)