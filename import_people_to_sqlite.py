#!/usr/bin/env python3
"""Import the 5-million-row synthetic people CSV into a separate SQLite table.

Place this script beside people_5m.csv and run:
    python import_people_to_sqlite.py

It imports in batches and uses INSERT OR IGNORE, so rerunning after an
interruption will skip person_id values already imported. It does not modify
VolleyVision's Player or PlayerStatistics tables.
"""
from __future__ import annotations

import csv
import itertools
import sqlite3
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "people_5m.csv"
DB_PATH = BASE_DIR / "volleyball.db"
BATCH_SIZE = 10_000
REPORT_EVERY = 100_000
REQUIRED_COLUMNS = [
    "person_id", "first_name", "last_name", "age", "city", "occupation"
]


def batches(iterator, size):
    while True:
        batch = list(itertools.islice(iterator, size))
        if not batch:
            return
        yield batch


def main() -> None:
    if not CSV_PATH.is_file():
        raise SystemExit(
            f"Не знайдено {CSV_PATH.name}. Поклади CSV поруч із цим скриптом."
        )

    started = time.time()
    connection = sqlite3.connect(DB_PATH)
    processed = 0

    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA busy_timeout=30000")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people_dataset (
                person_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                occupation TEXT NOT NULL
            )
            """
        )
        connection.commit()

        before_count = connection.execute(
            "SELECT COUNT(*) FROM people_dataset"
        ).fetchone()[0]
        print(f"База даних: {DB_PATH}")
        print(f"Записів у people_dataset до імпорту: {before_count:,}")
        print("Починаю імпорт пакетами по 10 000 записів...")

        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            actual_columns = reader.fieldnames or []
            missing = [col for col in REQUIRED_COLUMNS if col not in actual_columns]
            if missing:
                raise SystemExit(
                    "У CSV немає потрібних колонок: " + ", ".join(missing)
                )

            def convert_rows():
                for line_number, row in enumerate(reader, start=2):
                    try:
                        yield (
                            int(row["person_id"]),
                            row["first_name"].strip(),
                            row["last_name"].strip(),
                            int(row["age"]),
                            row["city"].strip(),
                            row["occupation"].strip(),
                        )
                    except (TypeError, ValueError) as error:
                        raise ValueError(
                            f"Некоректні дані в рядку CSV {line_number}: {error}"
                        ) from error

            insert_sql = """
                INSERT OR IGNORE INTO people_dataset
                (person_id, first_name, last_name, age, city, occupation)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            for batch in batches(convert_rows(), BATCH_SIZE):
                connection.executemany(insert_sql, batch)
                connection.commit()
                processed += len(batch)
                if processed % REPORT_EVERY == 0 or processed < BATCH_SIZE:
                    elapsed = time.time() - started
                    print(
                        f"Опрацьовано {processed:,} рядків CSV; "
                        f"час {elapsed:.1f} с",
                        flush=True,
                    )

        after_count = connection.execute(
            "SELECT COUNT(*) FROM people_dataset"
        ).fetchone()[0]
        elapsed = time.time() - started
        print("\nІмпорт завершено.")
        print(f"Рядків CSV опрацьовано: {processed:,}")
        print(f"Записів у people_dataset після імпорту: {after_count:,}")
        print(f"Додано нових записів: {after_count - before_count:,}")
        print(f"Розмір БД: {DB_PATH.stat().st_size / (1024 ** 2):.1f} МБ")
        print(f"Час виконання: {elapsed / 60:.1f} хв")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
