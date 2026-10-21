
from analytics.eda_and_cleaning import load_data, clean_data


def recommend_players(df, top_n=3):
    """
    Рекомендує найефективніших гравців за жадібним алгоритмом.

    df — таблиця зі статистикою гравців.
    top_n — максимальна кількість рекомендацій.
    """
    if top_n < 1:
        raise ValueError("Кількість рекомендацій має бути більшою за 0.")

    if df.empty:
        return df.copy()

    if "efficiency" not in df.columns:
        raise ValueError("У даних відсутній стовпець efficiency.")

    remaining = df.copy()
    recommendations = []

    while not remaining.empty and len(recommendations) < top_n:
        best_index = remaining["efficiency"].idxmax()
        recommendations.append(remaining.loc[best_index])
        remaining = remaining.drop(best_index)

    return (
        __import__("pandas")
        .DataFrame(recommendations)
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    players = clean_data(load_data())
    recommendations = recommend_players(players, top_n=3)

    print("\n--- РЕКОМЕНДОВАНІ ГРАВЦІ ---")
    columns = ["name", "position", "efficiency"]

    print(recommendations[columns].to_string(index=False))
