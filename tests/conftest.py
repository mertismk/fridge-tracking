"""
Конфигурация тестового окружения для pytest.
Предоставляет фикстуры для работы с тестовой базой данных и приложением Flask.
"""

import os
import pytest
from app import create_app, db
from sqlalchemy import text


is_ci = os.environ.get("CI", "false").lower() == "true"


@pytest.fixture(scope="session")
def app():
    """Фикстура создания тестового приложения с базой в памяти."""
    if is_ci:
        db_uri = "sqlite:///:memory:"
    else:
        db_user = os.environ.get("DB_USER", "postgres")
        db_password = os.environ.get("DB_PASSWORD", "2705")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "5432")
        db_name = os.environ.get("DB_NAME", "fridge_planner_test")

        use_sqlite = os.environ.get("DB_USE_SQLITE", "true").lower() == "true"

        if use_sqlite:
            db_uri = "sqlite:///:memory:"
        else:
            db_uri = f"postgresql://{db_user}:\
                    {db_password}@{db_host}:{db_port}/{db_name}"

    app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": db_uri,
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture(scope="function")
def db_session(app):
    """Предоставляет изолированную сессию для каждого теста."""
    with app.app_context():
        db.session.execute(text("DELETE FROM user"))
        db.session.execute(text("DELETE FROM product"))
        db.session.execute(text("DELETE FROM shopping_item"))
        db.session.commit()

        yield db.session

        db.session.remove()
        db.session.rollback()


@pytest.fixture
def client(app):
    """Клиент для тестирования."""
    return app.test_client()
