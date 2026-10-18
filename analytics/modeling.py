
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from analytics.eda_and_cleaning import load_data, clean_data


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "analytics" / "saved_models"
MODEL_PATH = MODEL_DIR / "player_classifier.joblib"

FEATURES = [
    "attacks",
    "aces",
    "blocks",
    "receptions",
    "errors",
]


def prepare_data(df):
    """Поділяє гравців на дві групи за ефективністю."""
    data = df.copy()

    data["performance"] = pd.qcut(
        data["efficiency"],
        q=2,
        labels=["нижча", "вища"],
    )

    return data


def train_model(df):
    """Навчає Random Forest і підбирає параметри через GridSearchCV."""
    data = prepare_data(df)

    if len(data) < 6:
        raise ValueError(
            "Для навчання моделі потрібно щонайменше 6 записів."
        )

    X = data[FEATURES]
    y = data["performance"].astype(str)

    # Перевіряємо, чи достатньо прикладів у кожній групі.
    class_counts = y.value_counts()

    if len(class_counts) < 2 or class_counts.min() < 2:
        raise ValueError(
            "Для навчання потрібні щонайменше два класи "
            "і по два приклади в кожному."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(random_state=42)

    parameters = {
        "n_estimators": [50, 100],
        "max_depth": [None, 5],
    }

    search = GridSearchCV(
        estimator=model,
        param_grid=parameters,
        cv=2,
        scoring="f1_macro",
        n_jobs=-1,
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    predictions = best_model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        ),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    return best_model, metrics, search.best_params_


if __name__ == "__main__":
    players = clean_data(load_data())

    model, metrics, best_params = train_model(players)

    print("\n--- RANDOM FOREST CLASSIFIER ---")
    print("Найкращі параметри:", best_params)

    print("\nМетрики моделі:")
    for metric, value in metrics.items():
        print(f"{metric.upper()}: {value:.3f}")

    print(f"\nМодель збережена: {MODEL_PATH}")
