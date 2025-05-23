# run.py
from app import create_app, db
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

db_user = os.environ.get("DB_USER", "postgres")
db_password = os.environ.get("DB_PASSWORD", "2705")
db_host = os.environ.get("DB_HOST", "db")
db_port = os.environ.get("DB_PORT", "5432")
db_name = os.environ.get("DB_NAME", "fridge_planner")

# Создаем директорию для метрик Gunicorn, если ее нет
prometheus_multiproc_dir = os.environ.get(
    "prometheus_multiproc_dir", "./prometheus_metrics_data"
)
if not os.path.exists(prometheus_multiproc_dir):
    os.makedirs(prometheus_multiproc_dir, exist_ok=True)

database_uri = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

app = create_app({"SQLALCHEMY_DATABASE_URI": database_uri})


def init_db():
    engine_uri = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    )

    try:
        engine = create_engine(engine_uri)
        db_exists = database_exists(engine.url.set(database=db_name))

        if not db_exists:
            print(f"Создание новой базы данных '{db_name}'...")
            create_database(engine.url.set(database=db_name))
            print(f"База данных '{db_name}' создана!")

        with app.app_context():
            try:
                db.create_all()
                print("Таблицы созданы через SQLAlchemy")
            except Exception as e:
                print(f"Ошибка при создании таблиц SQLAlchemy: {e}")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")


if __name__ == "__main__":
    init_db()
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=False)


def metrics_app(environ, start_response):
    """Точка входа для Gunicorn для обслуживания метрик на отдельном порту."""
    pass
