from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "players.csv"


def load_data(path=DATA_PATH):
    """Завантажує статистику гравців із CSV-файлу."""
    return pd.read_csv(path)


def clean_data(df):
    """Очищує та готує дані для машинного навчання."""
    df = df.copy()
    df = df.drop_duplicates()

    numeric_columns = [
        "age",
        "attacks",
        "aces",
        "blocks",
        "receptions",
        "errors",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        df[column] = df[column].fillna(df[column].median())

    df = df.dropna(subset=["name", "position"])

    df["efficiency"] = (
        df["attacks"]
        + 2 * df["aces"]
        + 2 * df["blocks"]
        + df["receptions"]
        - 2 * df["errors"]
    )

    return df.reset_index(drop=True)


def get_data_summary(df):
    """Повертає основну інформацію про набір даних."""
    return {
        "rows": len(df),
        "columns": df.columns.tolist(),
        "missing_values": df.isna().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "statistics": df.describe().to_dict(),
    }


if __name__ == "__main__":
    data = load_data()
    cleaned = clean_data(data)

    print("Перші п'ять записів:")
    print(cleaned.head())

    print("\nІнформація про дані:")
    print(get_data_summary(cleaned))