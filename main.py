from web_app.app import create_app
from web_app.models import db, Player, Match, PlayerStatistics, OperationLog


def show_players():
    players = Player.query.order_by(Player.number).all()

    print("\n--- ГРАВЦІ КОМАНДИ ---")

    if not players:
        print("Гравців поки немає.")
        return

    for player in players:
        print(
            f"№{player.number} | {player.name} | "
            f"{player.age} років | {player.position}"
        )


def add_player():
    print("\n--- ДОДАВАННЯ ГРАВЦЯ ---")

    try:
        name = input("Ім'я: ").strip()
        age = int(input("Вік: "))
        position = input("Позиція: ").strip()
        number = int(input("Номер гравця: "))

        if not name or not position:
            print("Ім'я та позиція обов'язкові.")
            return

        if not 10 <= age <= 60:
            print("Вік має бути від 10 до 60 років.")
            return

        if not 1 <= number <= 99:
            print("Номер має бути від 1 до 99.")
            return

        if Player.query.filter_by(number=number).first():
            print("Такий номер уже зайнятий.")
            return

        player = Player(
            name=name,
            age=age,
            position=position,
            number=number,
        )

        db.session.add(player)
        db.session.commit()

        log_operation(
            "players",
            "add",
            str(number),
            f"Додано гравця {name}",
        )

        print("Гравця успішно додано!")

    except ValueError:
        db.session.rollback()
        print("Помилка: введи коректні числові значення.")


def log_operation(structure, operation_type, value, description):
    log = OperationLog(
        structure=structure,
        operation_type=operation_type,
        value=value,
        description=description,
    )
    db.session.add(log)
    db.session.commit()


def show_statistics():
    records = (
        PlayerStatistics.query
        .join(Player)
        .order_by(Player.number)
        .all()
    )

    print("\n--- СТАТИСТИКА ГРАВЦІВ ---")

    if not records:
        print("Статистики поки немає.")
        return

    for record in records:
        print(
            f"{record.player.name}: "
            f"атаки — {record.attacks}, "
            f"ейси — {record.aces}, "
            f"блоки — {record.blocks}, "
            f"прийом — {record.receptions}, "
            f"помилки — {record.errors}"
        )


def add_statistics():
    print("\n--- ДОДАВАННЯ СТАТИСТИКИ ---")
    show_players()

    try:
        player_id = int(input("\nID гравця: "))
        player = db.session.get(Player, player_id)

        if player is None:
            print("Гравця з таким ID не знайдено.")
            return

        attacks = int(input("Атаки: "))
        aces = int(input("Ейси: "))
        blocks = int(input("Блоки: "))
        receptions = int(input("Прийом: "))
        errors = int(input("Помилки: "))

        values = [attacks, aces, blocks, receptions, errors]

        if any(value < 0 for value in values):
            print("Значення не можуть бути від'ємними.")
            return

        record = PlayerStatistics(
            player_id=player.id,
            attacks=attacks,
            aces=aces,
            blocks=blocks,
            receptions=receptions,
            errors=errors,
        )

        db.session.add(record)
        db.session.commit()

        log_operation(
            "statistics",
            "add",
            str(player.id),
            f"Додано статистику: {player.name}",
        )

        print("Статистику збережено!")

    except ValueError:
        db.session.rollback()
        print("Помилка: потрібно вводити цілі числа.")


def show_matches():
    matches = Match.query.order_by(Match.match_date.desc()).all()

    print("\n--- МАТЧІ КОМАНДИ ---")

    if not matches:
        print("Матчів поки немає.")
        return

    for match in matches:
        print(
            f"{match.match_date} | Проти {match.opponent} | "
            f"{match.team_score}:{match.opponent_score} | "
            f"{match.result}"
        )


def show_logs():
    logs = OperationLog.query.order_by(
        OperationLog.timestamp.desc()
    ).limit(20).all()

    print("\n--- ЖУРНАЛ ОПЕРАЦІЙ ---")

    if not logs:
        print("Записів поки немає.")
        return

    for log in logs:
        print(
            f"{log.timestamp} | {log.structure} | "
            f"{log.operation_type} | {log.description}"
        )


def main():
    app = create_app()

    with app.app_context():
        while True:
            print("\n" + "=" * 42)
            print("       VolleyVision")
            print("  Аналітика волейбольної команди")
            print("=" * 42)
            print("1. Переглянути гравців")
            print("2. Додати гравця")
            print("3. Додати статистику гравця")
            print("4. Переглянути статистику")
            print("5. Переглянути матчі")
            print("6. Журнал операцій")
            print("0. Вихід")

            choice = input("\nОбери дію: ").strip()

            if choice == "1":
                show_players()
            elif choice == "2":
                add_player()
            elif choice == "3":
                add_statistics()
            elif choice == "4":
                show_statistics()
            elif choice == "5":
                show_matches()
            elif choice == "6":
                show_logs()
            elif choice == "0":
                print("Роботу VolleyVision завершено.")
                break
            else:
                print("Невірний пункт меню.")

            input("\nНатисни Enter, щоб продовжити...")


if __name__ == "__main__":
    main()