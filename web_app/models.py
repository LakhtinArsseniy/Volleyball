from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False, unique=True)

    statistics = db.relationship(
        "PlayerStatistics",
        backref="player",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Player {self.name}>"


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.Date, nullable=False)
    team_score = db.Column(db.Integer, nullable=False)
    opponent_score = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Match vs {self.opponent}>"


class PlayerStatistics(db.Model):
    __tablename__ = "player_statistics"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(
        db.Integer,
        db.ForeignKey("players.id"),
        nullable=False
    )

    attacks = db.Column(db.Integer, default=0)
    aces = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    receptions = db.Column(db.Integer, default=0)
    errors = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Statistics player={self.player_id}>"


class OperationLog(db.Model):
    __tablename__ = "operation_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    structure = db.Column(db.String(50), nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<OperationLog {self.operation_type}>"