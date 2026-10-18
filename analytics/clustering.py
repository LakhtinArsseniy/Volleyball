import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from analytics.eda_and_cleaning import load_data, clean_data


FEATURES = [
    "attacks",
    "aces",
    "blocks",
    "receptions",
    "errors",
    "efficiency",
]


def cluster_players(df, n_clusters=3):
    """Групує гравців за їхніми статистичними показниками."""
    if df.empty:
        raise ValueError("Немає даних для кластеризації.")

    if not 1 <= n_clusters <= len(df):
        raise ValueError(
            "Кількість кластерів має бути від 1 "
            "до кількості гравців."
        )

    missing = [column for column in FEATURES if column not in df.columns]
    if missing:
        raise ValueError(f"Відсутні стовпці: {missing}")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[FEATURES])

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
    )

    result = df.copy()
    result["cluster"] = model.fit_predict(scaled_data)

    return result, model, scaler


if __name__ == "__main__":
    players = clean_data(load_data())
    clustered, model, scaler = cluster_players(players)

    print("\n--- КЛАСТЕРИЗАЦІЯ ГРАВЦІВ ---")
    print(
        clustered[
            ["name", "position", "efficiency", "cluster"]
        ].sort_values("cluster").to_string(index=False)
    )

    print("\nКількість гравців у групах:")
    print(clustered["cluster"].value_counts().sort_index())