import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path("data")
ARTIFACTS_DIR = Path("artifacts")
DATASET_PATH = DATA_DIR / "digital_deviation_ml_ready_yearly.csv"

TARGET_COLUMN = "digital_deviation_risk_score"
OLD_TARGET_COLUMN = "juvenile_offenders_share_pct"
DROP_COLUMNS = ["year", OLD_TARGET_COLUMN]

FEATURE_COLUMNS = [
    "internet_usage_pct",
    "social_media_usage_pct",
    "avg_time_online_hours",
    "social_media_time_share_pct",
    "internet_users_percent",
    "daily_internet_users",
    "internet_addiction_index",
    "stress_from_devices",
    "youth_online_activity",
    "avg_screen_time_hours",
]

# Веса признаков в итоговом индексе. Сумма весов равна 1.
FEATURE_WEIGHTS = {
    "internet_usage_pct": 0.06,
    "social_media_usage_pct": 0.14,
    "avg_time_online_hours": 0.16,
    "social_media_time_share_pct": 0.10,
    "internet_users_percent": 0.04,
    "daily_internet_users": 0.08,
    "internet_addiction_index": 0.20,
    "stress_from_devices": 0.14,
    "youth_online_activity": 0.04,
    "avg_screen_time_hours": 0.04,
}

# Фиксированные максимумы для нормализации. Так модель адекватно понимает низкие,
# средние и высокие значения даже если таких примеров мало в исходном датасете.
NORMALIZATION_MAX = {
    "internet_usage_pct": 100.0,
    "social_media_usage_pct": 100.0,
    "avg_time_online_hours": 12.0,
    "social_media_time_share_pct": 100.0,
    "internet_users_percent": 100.0,
    "daily_internet_users": 100.0,
    "internet_addiction_index": 100.0,
    "stress_from_devices": 100.0,
    "youth_online_activity": 100.0,
    "avg_screen_time_hours": 14.0,
}


def calculate_risk_score(df: pd.DataFrame) -> pd.Series:
    """Расчет индекса риска цифровой девиации от 0 до 100."""
    score = pd.Series(0.0, index=df.index)
    for col, weight in FEATURE_WEIGHTS.items():
        max_value = NORMALIZATION_MAX[col]
        normalized = (df[col].astype(float) / max_value).clip(0, 1)
        score += normalized * weight
    return (score * 100).clip(0, 100).round(2)


def generate_synthetic_scenarios(random_state: int = 42) -> pd.DataFrame:
    """Добавляет логичные учебные сценарии: низкий, средний и высокий риск.

    Это нужно, чтобы модель видела весь диапазон значений и не считала почти все
    входные данные высоким риском. Сценарии не заменяют исходные статистические
    данные, а расширяют обучающую выборку для корректной демонстрации API.
    """
    rng = np.random.default_rng(random_state)
    ranges = {
        "low": {
            "internet_usage_pct": (25, 50), "social_media_usage_pct": (15, 40),
            "avg_time_online_hours": (0.8, 2.8), "social_media_time_share_pct": (10, 30),
            "internet_users_percent": (25, 50), "daily_internet_users": (10, 35),
            "internet_addiction_index": (3, 25), "stress_from_devices": (3, 22),
            "youth_online_activity": (15, 40), "avg_screen_time_hours": (1.0, 3.2),
        },
        "medium": {
            "internet_usage_pct": (50, 72), "social_media_usage_pct": (42, 65),
            "avg_time_online_hours": (3.0, 5.4), "social_media_time_share_pct": (31, 55),
            "internet_users_percent": (50, 72), "daily_internet_users": (38, 62),
            "internet_addiction_index": (28, 55), "stress_from_devices": (25, 55),
            "youth_online_activity": (42, 68), "avg_screen_time_hours": (3.4, 6.2),
        },
        "high": {
            "internet_usage_pct": (73, 100), "social_media_usage_pct": (66, 100),
            "avg_time_online_hours": (5.6, 11.5), "social_media_time_share_pct": (56, 95),
            "internet_users_percent": (73, 100), "daily_internet_users": (63, 100),
            "internet_addiction_index": (56, 100), "stress_from_devices": (56, 100),
            "youth_online_activity": (69, 100), "avg_screen_time_hours": (6.3, 13.5),
        },
    }

    rows = []
    year = 2030
    for level, count in [("low", 50), ("medium", 70), ("high", 50)]:
        for _ in range(count):
            row = {"year": year, "scenario_level": level, "data_source": "synthetic_training_scenario"}
            for col, (left, right) in ranges[level].items():
                row[col] = round(float(rng.uniform(left, right)), 2)
            rows.append(row)
            year += 1
    synthetic = pd.DataFrame(rows)
    synthetic[TARGET_COLUMN] = calculate_risk_score(synthetic)
    return synthetic


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    original = pd.read_csv(DATASET_PATH).dropna().copy()
    original["scenario_level"] = "historical"
    original["data_source"] = "source_dataset"
    original[TARGET_COLUMN] = calculate_risk_score(original)

    synthetic = generate_synthetic_scenarios()
    df = pd.concat([original, synthetic], ignore_index=True)

    feature_columns = FEATURE_COLUMNS
    X = df[feature_columns]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    df.to_csv(DATA_DIR / "preprocessed.csv", index=False)
    X_train.to_csv(DATA_DIR / "predictors_train.csv", index=False)
    X_test.to_csv(DATA_DIR / "predictors_test.csv", index=False)
    y_train.to_csv(DATA_DIR / "target_train.csv", index=False)
    y_test.to_csv(DATA_DIR / "target_test.csv", index=False)

    pd.DataFrame(X_train_scaled, columns=feature_columns).to_csv(
        DATA_DIR / "predictors_scaled_train.csv", index=False
    )
    pd.DataFrame(X_test_scaled, columns=feature_columns).to_csv(
        DATA_DIR / "predictors_scaled_test.csv", index=False
    )

    joblib.dump(scaler, ARTIFACTS_DIR / "scaler.joblib")
    with open(ARTIFACTS_DIR / "feature_columns.json", "w", encoding="utf-8") as f:
        json.dump(feature_columns, f, ensure_ascii=False, indent=2)

    print("Предобработка завершена")
    print(f"Целевая переменная: {TARGET_COLUMN}")
    print(f"Исходных строк: {len(original)}")
    print(f"Синтетических сценариев: {len(synthetic)}")
    print(f"Всего строк после расширения: {len(df)}")
    print(f"Количество признаков: {len(feature_columns)}")
    print("Диапазон target:", float(df[TARGET_COLUMN].min()), "-", float(df[TARGET_COLUMN].max()))


if __name__ == "__main__":
    main()
