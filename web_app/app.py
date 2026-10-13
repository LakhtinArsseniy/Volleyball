
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from web_app.models import Player, PlayerStatistics, db


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "volleyball.db"


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{DATABASE_PATH}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    @app.route("/")
    def index():
        return redirect(url_for("players"))

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

                record = PlayerStatistics(
                    player_id=player.id,
                    **values,
                )

                db.session.add(record)
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
    with app.app_context():
        db.create_all()

    return app
