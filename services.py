from fastapi import HTTPException, status

from model import MODEL_VERSION, calculate_risk
from schemas import FarmRequest

ALLOWED_REGIONS = {"Krasnodar", "Rostov", "Stavropol"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high"}


def get_risk_level(score: float) -> str:
    if score < 0.3:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


def get_recommendation(level: str) -> str:
    if level == "low":
        return "Стандартное рассмотрение"
    if level == "medium":
        return "Требуется дополнительная проверка"
    return "Высокий риск. Требуется ручное рассмотрение"


def validate_region(region: str) -> None:
    if region not in ALLOWED_REGIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown region: {region}. "
                f"Allowed regions: {sorted(ALLOWED_REGIONS)}"
            ),
        )


def validate_risk_level(risk_level: str) -> None:
    if risk_level not in ALLOWED_RISK_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="risk_level must be 'low', 'medium' or 'high'",
        )


def build_prediction(request: FarmRequest, request_id: str) -> dict:
    score = calculate_risk(request)
    level = get_risk_level(score)
    recommendation = get_recommendation(level)

    return {
        "request_id": request_id,
        "farm_id": request.farm_id,
        "risk_score": score,
        "risk_level": level,
        "recommendation": recommendation,
        "model_version": MODEL_VERSION,
    }