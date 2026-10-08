from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from web_app.models import Player, db


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "volleyball.db"


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{DATABASE_PATH}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.route("/")
    def index():
        return redirect(url_for("players"))

    @app.route("/players")
    def players():
        all_players = Player.query.order_by(Player.number).all()

        return render_template(
            "players.html",
            players=all_players
        )

    @app.route("/players/add", methods=["GET", "POST"])
    def add_player():
        if request.method == "POST":
            name = request.form["name"]
            age = int(request.form["age"])
            position = request.form["position"]
            number = int(request.form["number"])

            player = Player(
                name=name,
                age=age,
                position=position,
                number=number
            )

            db.session.add(player)
            db.session.commit()

            return redirect(url_for("players"))

        return render_template("add_player.html")

    @app.route("/players/delete/<int:player_id>", methods=["POST"])
    def delete_player(player_id):
        player = db.get_or_404(Player, player_id)

        db.session.delete(player)
        db.session.commit()

        return redirect(url_for("players"))

    with app.app_context():
        db.create_all()

    return app