"""
Тесты для маршрутов приложения.
Проверяют корректность работы различных URL-путей.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models import User, Product
from app import db


@pytest.fixture
def test_client(app):
    """Клиент для тестирования."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя."""
    user = User(username="testroutes", email="testroutes@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_products(db_session, test_user):
    """Создает тестовые продукты."""
    now = datetime.now(timezone.utc)

    products = [
        Product(
            name="Тестовый продукт 1",
            category="Овощи",
            quantity=1.0,
            unit="кг",
            expiry_date=now + timedelta(days=5),
            user_id=test_user.id,
        ),
        Product(
            name="Тестовый продукт 2",
            category="Мясо",
            quantity=0.5,
            unit="кг",
            expiry_date=now + timedelta(days=2),
            user_id=test_user.id,
        ),
        Product(
            name="Истекший продукт",
            category="Молочные",
            quantity=0.5,
            unit="л",
            expiry_date=now - timedelta(days=1),
            user_id=test_user.id,
        ),
    ]

    db_session.add_all(products)
    db_session.commit()

    return products


def test_home_page_redirect(test_client):
    """Тест перенаправления с главной страницы для неавторизованных \
        пользователей."""
    response = test_client.get("/")
    # без авторизации должно быть перенаправление на страницу входа
    assert (
        response.status_code == 302
    ), "Главная страница должна перенаправлять неавторизованных пользователей"
    # проверяем, что перенаправление идет на страницу входа
    assert "/login" in response.headers.get(
        "Location", ""
    ), "Перенаправление должно вести на страницу входа"


def test_login_route(test_client):
    """Тест маршрута авторизации."""
    # проверяем GET запрос - должна отображаться страница входа
    response = test_client.get("/login")
    assert (
        response.status_code == 200
    ), "Страница входа должна возвращать статус 200"
    assert "Вход" in response.data.decode(
        "utf-8"
    ), "Страница должна содержать заголовок формы входа"

    # проверяем POST запрос с правильными данными
    test_user = User(username="logintest", email="logintest@example.com")
    test_user.set_password("password")
    db.session.add(test_user)
    db.session.commit()

    login_data = {"username_or_email": "logintest", "password": "password"}
    response = test_client.post(
        "/login",
        data=login_data,
        follow_redirects=True,
    )

    assert (
        response.status_code == 200
    ), "После успешного входа должен быть статус 200"
    assert "Вы успешно вошли" in response.data.decode(
        "utf-8"
    ), "Должно быть сообщение об успешном входе"


def test_register_route(test_client, db_session):
    """Тест маршрута регистрации."""
    # проверяем GET запрос - должна отображаться страница регистрации
    response = test_client.get("/register")
    assert (
        response.status_code == 200
    ), "Страница регистрации должна возвращать статус 200"
    assert "Регистрация" in response.data.decode(
        "utf-8"
    ), "Страница должна содержать заголовок формы регистрации"

    # проверяем POST запрос с правильными данными
    response = test_client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert (
        response.status_code == 200
    ), "После успешной регистрации должен быть статус 200"
    assert "Регистрация прошла успешно" in response.data.decode(
        "utf-8"
    ), "Должно быть сообщение об успешной регистрации"

    # проверяем, что пользователь создан
    user = User.query.filter_by(username="newuser").first()
    assert user is not None, "Пользователь должен быть создан в БД"
    assert (
        user.email == "newuser@example.com"
    ), "Email пользователя должен быть сохранен"
    assert user.check_password(
        "password123"
    ), "Пароль должен быть корректно установлен"


def test_products_route(test_client, test_user, test_products):
    """Тест функциональности работы с продуктами."""
    # сначала авторизуемся
    test_client.post(
        "/login",
        data={"username_or_email": test_user.username, "password": "password"},
    )

    # проверяем страницу добавления продукта
    response = test_client.get("/add_product")
    assert (
        response.status_code == 200
    ), "Страница добавления продукта должна возвращать статус 200"

    # добавляем новый продукт
    now = datetime.now(timezone.utc)
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    response = test_client.post(
        "/add_product",
        data={
            "name": "Новый продукт",
            "category": "Фрукты",
            "quantity": "2.5",
            "unit": "кг",
            "expiry_date": tomorrow,
        },
        follow_redirects=True,
    )

    assert (
        response.status_code == 200
    ), "После добавления продукта должен быть статус 200"
    assert "Новый продукт" in response.data.decode(
        "utf-8"
    ), "Новый продукт должен отображаться на странице"

    # Проверяем, что продукт добавлен в БД
    product = Product.query.filter_by(
        name="Новый продукт", user_id=test_user.id
    ).first()
    assert product is not None, "Продукт должен быть сохранен в БД"
    assert (
        product.category == "Фрукты"
    ), "Категория продукта должна совпадать с указанной"
    assert (
        product.quantity == 2.5
    ), "Количество продукта должно совпадать с указанным"


def test_delete_product_route(test_client, test_user, test_products):
    """Тест удаления продукта."""
    test_client.post(
        "/login",
        data={"username_or_email": test_user.username, "password": "password"},
    )

    product_id = test_products[0].id

    response = test_client.get(
        f"/delete_product/{product_id}", follow_redirects=True
    )

    assert (
        response.status_code == 200
    ), "После удаления продукта должен быть статус 200"

    # проверяем, что продукт удален из БД
    deleted_product = Product.query.get(product_id)
    assert deleted_product is None, "Продукт должен быть удален из БД"
