import json
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware


ARTIFACTS_DIR = Path("artifacts")
MODEL_PATH = ARTIFACTS_DIR / "linear_regression_model.joblib"
SCALER_PATH = ARTIFACTS_DIR / "scaler.joblib"
PARAMS_PATH = ARTIFACTS_DIR / "model_params.json"

app = FastAPI(
    title="Digital Deviation Forecast API",
    description="API для прогноза индекса цифровой подростковой девиации в информационной сфере",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
    internet_usage_pct: float = Field(..., description="Доля пользователей интернета, %")
    social_media_usage_pct: float = Field(..., description="Доля пользователей социальных сетей, %")
    avg_time_online_hours: float = Field(..., description="Среднее время онлайн, часов в день")
    social_media_time_share_pct: float = Field(..., description="Доля времени в интернете, приходящаяся на соцсети, %")
    internet_users_percent: float = Field(..., description="Процент пользователей интернета, %")
    daily_internet_users: float = Field(..., description="Доля ежедневных пользователей интернета, %")
    internet_addiction_index: float = Field(..., description="Индекс интернет-зависимости")
    stress_from_devices: float = Field(..., description="Индекс стресса от цифровых устройств")
    youth_online_activity: float = Field(..., description="Индекс онлайн-активности молодежи")
    avg_screen_time_hours: float = Field(..., description="Среднее экранное время, часов в день")


class Response(BaseModel):
    result: float
    level: str
    description: str


def load_artifacts():
    missing = [str(path) for path in [MODEL_PATH, SCALER_PATH, PARAMS_PATH] if not path.exists()]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Не найдены файлы обученной модели. Сначала выполните команды: "
                "python preprocess.py && python train_model.py. "
                f"Отсутствуют: {missing}"
            ),
        )

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    with open(PARAMS_PATH, "r", encoding="utf-8") as f:
        params = json.load(f)
    return model, scaler, params


def interpret_result(value: float) -> Dict[str, str]:
    if value < 35:
        return {
            "level": "низкий",
            "description": "Прогнозируемый уровень цифровой девиации низкий.",
        }
    if value < 65:
        return {
            "level": "средний",
            "description": "Прогнозируемый уровень цифровой девиации находится в среднем диапазоне.",
        }
    return {
        "level": "высокий",
        "description": "Прогнозируемый уровень цифровой девиации высокий из-за повышенных цифровых факторов риска.",
    }


@app.get("/")
def root():
    return {
        "message": "Digital Deviation Forecast API работает",
        "docs": "/docs",
        "endpoint": "/deviant-forecast",
    }


@app.get("/features")
def features():
    _, _, params = load_artifacts()
    return {
        "target": params.get("target"),
        "features": params.get("feature_columns"),
        "metrics": params.get("metrics"),
    }


@app.post("/deviant-forecast", response_model=List[Response])
def deviant_forecast(request: List[Request]) -> List[Response]:
    model, scaler, params = load_artifacts()
    feature_columns = params["feature_columns"]

    rows = []
    for item in request:
        row = item.model_dump() if hasattr(item, "model_dump") else item.dict()
        rows.append([row[col] for col in feature_columns])

    df_req = pd.DataFrame(rows, columns=feature_columns)
    scaled_array = scaler.transform(df_req)
    scaled_df = pd.DataFrame(scaled_array, columns=feature_columns)
    predictions = model.predict(scaled_df)

    response = []
    for pred in predictions:
        value = round(max(0, min(100, float(pred))), 2)
        interpretation = interpret_result(value)
        response.append({
            "result": value,
            "level": interpretation["level"],
            "description": interpretation["description"],
        })

    return response
