"""
Конфигурация тестового окружения для pytest.
Предоставляет фикстуры для работы с тестовой базой данных и приложением Flask.
"""
import os
import pytest
from app import create_app, db


# Проверка CI-окружения (Jenkins или другая CI-система)
is_ci = os.environ.get("CI", "false").lower() == "true" or os.environ.get("JENKINS_URL") is not None


@pytest.fixture(scope="session")
def app():
    """
    Создает экземпляр приложения Flask для тестирования.
    В CI используем SQLite в памяти, иначе используем конфигурацию из app/__init__.py
    """
    # В CI используем SQLite в памяти
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False  # Отключаем CSRF защиту для тестов
    }
    
    # Создаем приложение с тестовой конфигурацией
    app = create_app(test_config)
    
    # Создаем тестовый контекст приложения
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        yield app
        # Удаляем все таблицы
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(app):
    """
    Создает сессию базы данных для теста и выполняет очистку после теста.
    """
    # Начинаем транзакцию
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Привязываем сессию к текущей транзакции
    session = db.session
    session.bind = connection
    
    yield session
    
    # Откатываем изменения и закрываем соединение
    session.close()
    transaction.rollback()
    connection.close() 