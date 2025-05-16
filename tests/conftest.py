"""
Конфигурация тестового окружения для pytest.
Предоставляет фикстуры для работы с тестовой базой данных и приложением Flask.
"""
import os
import pytest
from sqlalchemy import create_engine, text
from app import create_app, db
from datetime import datetime


# Параметры подключения к тестовой базе данных
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "2705")
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = f"{os.environ.get('DB_NAME', 'fridge_planner')}_test"

# Строка подключения к тестовой PostgreSQL
TEST_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


@pytest.fixture(scope="session")
def database():
    """
    Создает тестовую базу данных перед выполнением тестов и удаляет ее после.
    Использует административное подключение к PostgreSQL.
    """
    # Создаем движок для подключения к основной БД PostgreSQL
    admin_engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
    )
    
    # Создаем тестовую базу данных
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        # Удаляем БД если она уже существует
        conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
        # Создаем новую тестовую БД
        conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
    
    yield
    
    # Закрываем все соединения и удаляем тестовую БД
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))


@pytest.fixture(scope="session")
def app(database):
    """
    Создает экземпляр приложения Flask для тестирования.
    Настраивает подключение к тестовой базе данных.
    """
    # Конфигурация для тестов
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False  # Отключаем CSRF защиту для тестов
    })
    
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