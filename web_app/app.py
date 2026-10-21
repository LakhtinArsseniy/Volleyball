import os
import sqlite3
from time import perf_counter
from statistics import median
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for, session
from sqlalchemy.exc import IntegrityError

from web_app.models import Player, PlayerStatistics, OperationLog, db


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "volleyball.db"


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "volleyvision-local-development-key"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    @app.route("/")
    def index():
        players_list = Player.query.order_by(Player.number).all()

        records = (
            PlayerStatistics.query
            .join(Player)
            .order_by(PlayerStatistics.id.desc())
            .all()
        )

        efficiencies = [
            r.attacks + 2 * r.aces + 2 * r.blocks
            + r.receptions - 2 * r.errors
            for r in records
        ]

        average_efficiency = (
            round(sum(efficiencies) / len(efficiencies), 1)
            if efficiencies else 0
        )

        return render_template(
            "dashboard.html",
            players=players_list,
            records=records,
            average_efficiency=average_efficiency,
        )

    @app.route("/players")
    def players():
        all_players = Player.query.order_by(Player.number).all()

        return render_template(
            "players.html",
            players=all_players,
        )

    @app.route("/players/add", methods=["GET", "POST"])
    def add_player():
        if request.method == "POST":
            try:
                name = request.form["name"].strip()
                age = int(request.form["age"])
                position = request.form["position"].strip()
                number = int(request.form["number"])

                if not name or not position:
                    return "Ім'я та позиція обов'язкові", 400

                if not 10 <= age <= 60:
                    return "Вік має бути від 10 до 60 років", 400

                if not 1 <= number <= 99:
                    return "Номер має бути від 1 до 99", 400

                player = Player(
                    name=name,
                    age=age,
                    position=position,
                    number=number,
                )

                db.session.add(player)

                db.session.add(OperationLog(
                    structure="players",
                    operation_type="add",
                    value=str(number),
                    description=f"Додано гравця {name}",
                ))

                db.session.commit()
                return redirect(url_for("players"))

            except ValueError:
                db.session.rollback()
                return "Перевір правильність введених чисел", 400

            except IntegrityError:
                db.session.rollback()
                return "Гравець із таким номером уже існує", 400

        return render_template("add_player.html")

    @app.route("/players/delete/<int:player_id>", methods=["POST"])
    def delete_player(player_id):
        player = db.get_or_404(Player, player_id)

        db.session.add(OperationLog(
            structure="players",
            operation_type="delete",
            value=str(player.number),
            description=f"Видалено гравця {player.name}",
        ))

        db.session.delete(player)
        db.session.commit()

        return redirect(url_for("players"))

    @app.route("/statistics", methods=["GET", "POST"])
    def statistics():
        players_list = Player.query.order_by(Player.number).all()

        if request.method == "POST":
            try:
                player_id = int(request.form["player_id"])

                fields = [
                    "attacks",
                    "aces",
                    "blocks",
                    "receptions",
                    "errors",
                ]

                values = {}

                for field in fields:
                    value = int(request.form[field])

                    if value < 0:
                        raise ValueError

                    values[field] = value

                player = db.session.get(Player, player_id)

                if player is None:
                    return "Гравця не знайдено", 404

                record = PlayerStatistics(player_id=player.id, **values)
                db.session.add(record)

                db.session.add(OperationLog(
                    structure="statistics",
                    operation_type="add",
                    value=str(player.id),
                    description=(
                        f"Додано статистику гравця {player.name}: "
                        f"атаки={values['attacks']}, "
                        f"ейси={values['aces']}, "
                        f"блоки={values['blocks']}, "
                        f"прийоми={values['receptions']}, "
                        f"помилки={values['errors']}"
                    ),
                ))

                db.session.commit()

                return redirect(url_for("statistics"))

            except (ValueError, KeyError):
                db.session.rollback()
                return "Введи коректні невід'ємні цілі числа", 400

        records = (
            PlayerStatistics.query
            .join(Player)
            .order_by(PlayerStatistics.id.desc())
            .all()
        )

        return render_template(
            "statistics.html",
            players=players_list,
            records=records,
        )



    @app.route("/queue", methods=["GET", "POST"])
    def queue_page():
        from web_app.structures import FIFOQueue, LIFOStack

        queue_items = session.get("queue_items", [])
        stack_items = session.get("stack_items", [])

        if request.method == "POST":
            action = request.form.get("action")
            value = request.form.get("value", "").strip()
            message = ""
            log_entry = None

            if action == "queue_add":
                if value:
                    queue = FIFOQueue()
                    for item in queue_items:
                        queue.enqueue(item)
                    queue.enqueue(value)

                    queue_items.append(value)
                    message = f"До черги додано: {value}"

                    log_entry = OperationLog(
                        structure="FIFOQueue",
                        operation_type="enqueue",
                        value=value,
                        description="Додано елемент до FIFO-черги",
                    )
                else:
                    message = "Введи значення для черги."

            elif action == "queue_remove":
                if queue_items:
                    queue = FIFOQueue()
                    for item in queue_items:
                        queue.enqueue(item)

                    removed = queue.dequeue()
                    queue_items.pop(0)
                    message = f"З черги вилучено: {removed}"

                    log_entry = OperationLog(
                        structure="FIFOQueue",
                        operation_type="dequeue",
                        value=str(removed),
                        description="Вилучено перший елемент FIFO-черги",
                    )
                else:
                    message = "Черга порожня."

            elif action == "stack_add":
                if value:
                    stack = LIFOStack()
                    for item in stack_items:
                        stack.push(item)
                    stack.push(value)

                    stack_items.append(value)
                    message = f"До стека додано: {value}"

                    log_entry = OperationLog(
                        structure="LIFOStack",
                        operation_type="push",
                        value=value,
                        description="Додано елемент до LIFO-стека",
                    )
                else:
                    message = "Введи значення для стека."

            elif action == "stack_remove":
                if stack_items:
                    stack = LIFOStack()
                    for item in stack_items:
                        stack.push(item)

                    removed = stack.pop()
                    stack_items.pop()
                    message = f"Зі стека вилучено: {removed}"

                    log_entry = OperationLog(
                        structure="LIFOStack",
                        operation_type="pop",
                        value=str(removed),
                        description="Вилучено верхній елемент LIFO-стека",
                    )
                else:
                    message = "Стек порожній."

            if log_entry is not None:
                try:
                    db.session.add(log_entry)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    app.logger.exception(
                        "Не вдалося записати операцію до журналу"
                    )
                    message += " Увага: операцію не вдалося записати до журналу."

            session["queue_items"] = queue_items
            session["stack_items"] = stack_items
            session["structure_message"] = message

            return redirect(url_for("queue_page"))

        message = session.pop("structure_message", "")

        return render_template(
            "queue.html",
            queue_items=queue_items,
            stack_items=stack_items,
            message=message,
        )


    @app.route("/logs")
    def operation_logs():
        logs = (
            OperationLog.query
            .order_by(OperationLog.timestamp.desc(), OperationLog.id.desc())
            .limit(100)
            .all()
        )

        total_logs = OperationLog.query.count()

        return render_template(
            "operation_logs.html",
            logs=logs,
            total_logs=total_logs,
        )



    with app.app_context():
        db.create_all()


    @app.route("/analytics")
    def analytics():
        players_list = Player.query.order_by(Player.number).all()

        records = PlayerStatistics.query.all()

        player_stats = {}
        for record in records:
            player = db.session.get(Player, record.player_id)
            if player is None:
                continue

            if player.id not in player_stats:
                player_stats[player.id] = {
                    "name": player.name,
                    "attacks": 0,
                    "aces": 0,
                    "blocks": 0,
                    "receptions": 0,
                    "errors": 0,
                }

            stats = player_stats[player.id]
            stats["attacks"] += record.attacks
            stats["aces"] += record.aces
            stats["blocks"] += record.blocks
            stats["receptions"] += record.receptions
            stats["errors"] += record.errors

        analytics_data = list(player_stats.values())

        for item in analytics_data:
            item["efficiency"] = (
                item["attacks"]
                + 2 * item["aces"]
                + 2 * item["blocks"]
                + item["receptions"]
                - 2 * item["errors"]
            )

        analytics_data.sort(
            key=lambda item: item["efficiency"],
            reverse=True,
        )

        return render_template(
            "analytics.html",
            players=players_list,
            analytics_data=analytics_data,
        )


    @app.route("/benchmark")
    def benchmark():
        from web_app.algorithms import (
            bubble_sort,
            quick_sort,
            linear_search,
            binary_search,
        )

        with sqlite3.connect(DATABASE_PATH) as connection:
            dataset_count = connection.execute(
                "SELECT COUNT(*) FROM people_dataset"
            ).fetchone()[0]

            rows = connection.execute(
                "SELECT age FROM people_dataset LIMIT 20000"
            ).fetchall()

        values = [int(row[0]) for row in rows if row[0] is not None]
        small_values = values[:1000]

        results = []

        def measure(name, count, operation, note):
            times = []
            for _ in range(5):
                start = perf_counter()
                operation()
                elapsed = perf_counter() - start
                times.append(elapsed)

            results.append({
                "name": name,
                "count": count,
                "seconds": median(times),
                "note": note,
                "runs": len(times),
            })

        if small_values:
            measure(
                "Bubble Sort",
                len(small_values),
                lambda: bubble_sort(small_values.copy()),
                "Сортування невеликої вибірки",
            )

            measure(
                "Quick Sort",
                len(small_values),
                lambda: quick_sort(small_values.copy()),
                "Та сама вибірка для порівняння",
            )

        if values:
            measure(
                "Quick Sort — велика вибірка",
                len(values),
                lambda: quick_sort(values.copy()),
                "Сортування до 20 000 значень",
            )

            sorted_values = quick_sort(values.copy())
            missing_value = max(values) + 1

            measure(
                "Linear Search",
                len(values),
                lambda: linear_search(values, missing_value),
                "Пошук відсутнього значення",
            )

            measure(
                "Binary Search",
                len(sorted_values),
                lambda: binary_search(sorted_values, missing_value),
                "Пошук у відсортованих даних",
            )

        return render_template(
            "benchmark.html",
            dataset_count=dataset_count,
            sample_count=len(values),
            results=results,
        )



    return app
