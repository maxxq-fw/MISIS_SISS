from typing import Dict, List, Optional

predictions: Dict[str, dict] = {}


def save_prediction(request_id: str, result: dict) -> None:
    predictions[request_id] = result


def get_prediction_by_id(request_id: str) -> Optional[dict]:
    return predictions.get(request_id)


def list_predictions(
    limit: int = 10,
    risk_level: Optional[str] = None,
) -> List[dict]:
    values = list(predictions.values())

    if risk_level is not None:
        values = [item for item in values if item["risk_level"] == risk_level]

    return values[:limit]