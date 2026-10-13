import pytest

from web_app.app import create_app
from web_app.models import db, Player, PlayerStatistics


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test_volleyball.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        player = Player(
            name="Тестовий гравець",
            age=20,
            position="Догравальник",
            number=7,
        )
        db.session.add(player)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_statistics_page_opens(client):
    response = client.get("/statistics")

    assert response.status_code == 200


def test_save_player_statistics(client, app):
    with app.app_context():
        player = Player.query.filter_by(number=7).first()
        player_id = player.id

    response = client.post(
        "/statistics",
        data={
            "player_id": str(player_id),
            "attacks": "15",
            "aces": "3",
            "blocks": "2",
            "receptions": "10",
            "errors": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        record = PlayerStatistics.query.filter_by(
            player_id=player_id
        ).first()

        assert record is not None
        assert record.attacks == 15
        assert record.aces == 3


def test_negative_statistics_are_rejected(client, app):
    with app.app_context():
        player = Player.query.filter_by(number=7).first()
        player_id = player.id

    response = client.post(
        "/statistics",
        data={
            "player_id": str(player_id),
            "attacks": "-1",
            "aces": "0",
            "blocks": "0",
            "receptions": "0",
            "errors": "0",
        },
    )

    assert response.status_code == 400


def test_nonexistent_player_is_rejected(client):
    response = client.post(
        "/statistics",
        data={
            "player_id": "99999",
            "attacks": "10",
            "aces": "2",
            "blocks": "1",
            "receptions": "5",
            "errors": "0",
        },
    )

    assert response.status_code == 404


def test_multiple_statistics_records_are_preserved(client, app):
    with app.app_context():
        player = Player.query.filter_by(number=7).first()
        player_id = player.id

    for attacks in ("10", "20"):
        response = client.post(
            "/statistics",
            data={
                "player_id": str(player_id),
                "attacks": attacks,
                "aces": "2",
                "blocks": "1",
                "receptions": "5",
                "errors": "0",
            },
        )
        assert response.status_code == 302

    with app.app_context():
        records = PlayerStatistics.query.filter_by(
            player_id=player_id
        ).all()

        assert len(records) == 2
        assert sorted(record.attacks for record in records) == [10, 20]
