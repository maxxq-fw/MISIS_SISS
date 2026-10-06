import logging
import time
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request, status

from model import MODEL_NAME, MODEL_READY, MODEL_TYPE, MODEL_VERSION
from schemas import (
    FarmRequest,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)
from services import build_prediction, validate_region, validate_risk_level
from storage import get_prediction_by_id, list_predictions, save_prediction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agro Scoring API",
    description="REST API для оценки риска сельскохозяйственных предприятий.",
    version="1.0.0",
)


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 6))
    return response


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверка состояния API",
    description="Используется для проверки того, что REST API запущен и отвечает.",
)
def health():
    return {"status": "ok"}


@app.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Информация о модели",
    description="Возвращает название, версию, тип и текущее состояние модели.",
)
def model_info():
    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_type": MODEL_TYPE,
        "status": "ready" if MODEL_READY else "unavailable",
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Оценить риск хозяйства",
    description=(
        "Принимает характеристики хозяйства, выполняет валидацию, "
        "инференс модели и возвращает оценку риска."
    ),
)
def predict(request: FarmRequest):
    if not MODEL_READY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is temporarily unavailable",
        )

    validate_region(request.region)

    logger.info("Prediction request received | farm_id=%s", request.farm_id)

    request_id = str(uuid.uuid4())
    result = build_prediction(request, request_id)

    save_prediction(request_id, result)

    logger.info(
        "Prediction completed | request_id=%s | farm_id=%s | "
        "risk_score=%s | risk_level=%s",
        request_id,
        request.farm_id,
        result["risk_score"],
        result["risk_level"],
    )

    return result


@app.get(
    "/predictions",
    response_model=List[PredictionResponse],
    summary="Получить список прогнозов",
    description=(
        "Возвращает список выполненных прогнозов. "
        "Поддерживает ограничение количества результатов "
        "и фильтрацию по уровню риска."
    ),
)
def get_predictions(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Максимальное количество результатов",
    ),
    risk_level: Optional[str] = Query(
        default=None,
        description="Фильтр по категории риска: low, medium или high",
    ),
):
    if risk_level is not None:
        validate_risk_level(risk_level)

    return list_predictions(limit=limit, risk_level=risk_level)


@app.get(
    "/predictions/{request_id}",
    response_model=PredictionResponse,
    summary="Получить прогноз по request_id",
    description="Возвращает сохраненный прогноз по его уникальному идентификатору.",
)
def get_prediction(request_id: str):
    result = get_prediction_by_id(request_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)