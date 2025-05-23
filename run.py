# run.py
from app import create_app, db, models  
import os
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database

db_user = os.environ.get("DB_USER", "postgres")
db_password = os.environ.get("DB_PASSWORD", "2705")
db_host = os.environ.get("DB_HOST", "db")
db_port = os.environ.get("DB_PORT", "5432")
db_name = os.environ.get("DB_NAME", "fridge_planner")

database_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

app = create_app({"SQLALCHEMY_DATABASE_URI": database_uri})


def init_db():
    engine_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"

    try:
        engine = create_engine(engine_uri)
        db_exists = database_exists(engine.url.set(database=db_name))

        if not db_exists:
            print(f"Создание новой базы данных '{db_name}'...")
            create_database(engine.url.set(database=db_name))
            print(f"База данных '{db_name}' создана!")

        db_engine = create_engine(database_uri)

        with app.app_context():
            try:
                db.create_all()
                print("Таблицы созданы через SQLAlchemy")
            except Exception as e:
                print(f"Ошибка при создании таблиц SQLAlchemy: {e}")

        sql_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "db_init.sql"
        )
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            try:
                with db_engine.connect() as conn:
                    conn.execute(text(sql_script))
                    conn.commit()
                print("База данных успешно инициализирована через SQL-скрипт!")
            except Exception as e:
                print(f"Ошибка при выполнении SQL-скрипта: {e}")
        else:
            print(f"Файл инициализации БД не найден: {sql_path}")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
