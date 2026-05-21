import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


DATA_DIR = Path("data")
ARTIFACTS_DIR = Path("artifacts")


def main() -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    X_train = pd.read_csv(DATA_DIR / "predictors_scaled_train.csv")
    X_test = pd.read_csv(DATA_DIR / "predictors_scaled_test.csv")
    y_train = pd.read_csv(DATA_DIR / "target_train.csv").values.ravel()
    y_test = pd.read_csv(DATA_DIR / "target_test.csv").values.ravel()

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    params = {
        "model_type": "LinearRegression",
        "coeffs": [float(x) for x in model.coef_],
        "shift": float(model.intercept_),
        "feature_columns": list(X_train.columns),
        "metrics": {
            "MAE": float(mae),
            "MSE": float(mse),
            "R2": float(r2),
        },
        "target": "digital_deviation_risk_score",
    }

    joblib.dump(model, ARTIFACTS_DIR / "linear_regression_model.joblib")
    with open(ARTIFACTS_DIR / "model_params.json", "w", encoding="utf-8") as f:
        json.dump(params, f, ensure_ascii=False, indent=2)

    print("Модель обучена")
    print("Коэффициенты модели:")
    print(params["coeffs"])
    print("Свободный член / shift:")
    print(params["shift"])
    print("Метрики качества:")
    print(params["metrics"])
    print("\nВажно: датасет небольшой, поэтому метрики используются как учебная демонстрация, а не как точная научная оценка.")


if __name__ == "__main__":
    main()
