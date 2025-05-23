"""
Юнит-тесты для функций из модуля utils.py.
Тестируют утилиты для работы с продуктами и рекомендациями.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app import db
from app.models import Product, User
from app.utils import (
    get_expiring_products,
    get_recipe_suggestions,
    get_expired_message,
    suggest_shopping_items,
)
from unittest.mock import patch


@pytest.fixture
def test_user(db_session):
    user = User(username="testutil", email="testutil@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_products(db_session, test_user):
    now = datetime.now(timezone.utc)

    expiring_soon = Product(
        name="Скоро испортится",
        category="Овощи",
        quantity=1.0,
        unit="кг",
        expiry_date=now + timedelta(days=2),
        user_id=test_user.id,
    )

    expiring_later = Product(
        name="Испортится нескоро",
        category="Мясо",
        quantity=0.5,
        unit="кг",
        expiry_date=now + timedelta(days=5),
        user_id=test_user.id,
    )

    expired = Product(
        name="Уже испортился",
        category="Молочные продукты",
        quantity=0.5,
        unit="л",
        expiry_date=now - timedelta(days=1),
        user_id=test_user.id,
    )

    fruit = Product(
        name="Банан",
        category="Фрукты",
        quantity=3.0,
        unit="шт",
        expiry_date=now + timedelta(days=4),
        user_id=test_user.id,
    )

    db_session.add_all([expiring_soon, expiring_later, expired, fruit])
    db_session.commit()

    return {
        "expiring_soon": expiring_soon,
        "expiring_later": expiring_later,
        "expired": expired,
        "fruit": fruit,
        "all": [expiring_soon, expiring_later, expired, fruit],
    }


def test_get_expiring_products(test_products):
    """Тест функции получения продуктов с истекающим сроком годности."""
    expiring = get_expiring_products(test_products["all"])
    assert (
        len(expiring) == 1
    ), (
        "Должен быть только один продукт с истекающим сроком "
        "годности (до 3 дней)"
    )
    assert (
        expiring[0].name == "Скоро испортится"
    ), "Неверный продукт в списке истекающих"

    expiring_more = get_expiring_products(test_products["all"], days=6)
    assert len(expiring_more) == 3, (
        "Должно быть три продукта с истекающим сроком "
        "годности (до 6 дней)"
    )
    names = [p.name for p in expiring_more]
    assert (
        "Скоро испортится" in names
    ), "Отсутствует ожидаемый продукт в списке истекающих"
    assert (
        "Испортится нескоро" in names
    ), "Отсутствует ожидаемый продукт в списке истекающих"
    assert (
        "Банан" in names
    ), "Отсутствует ожидаемый продукт в списке истекающих"


def test_get_recipe_suggestions(test_products):
    """Тест функции получения рекомендаций рецептов."""
    suggestions = get_recipe_suggestions(test_products["all"])

    assert (
        len(suggestions) >= 1
    ), "Должно быть как минимум одно предложение рецепта"

    meat_recipe = next(
        (s for s in suggestions if s["name"] == "Мясо с овощами"), None
    )
    assert meat_recipe is not None, "Должен быть рецепт 'Мясо с овощами'"

    products_in_recipe = meat_recipe["products"]
    assert (
        "Скоро испортится" in products_in_recipe
    ), "Продукт из категории 'Овощи' не включен в рецепт"
    assert (
        "Испортится нескоро" in products_in_recipe
    ), "Продукт из категории 'Мясо' не включен в рецепт"

    assert (
        "Уже испортился" not in products_in_recipe
    ), "Просроченный продукт не должен быть в рецепте"


def test_get_expired_message(test_products):
    """Тест функции получения сообщения для просроченного продукта."""
    expired_product = test_products["expired"]

    # функция-заглушка для возврата сообщения
    def mock_choice(messages_list):
        for msg in messages_list:
            if "решил стать новым видом сыра с плесенью" in msg:
                return msg
        return messages_list[
            0
        ]  # возвращаем первое сообщение как запасной вариант

    # применяем патч
    with patch("app.utils.secrets.choice", side_effect=mock_choice):
        result = get_expired_message(expired_product)
        expected = (
            f"Кажется, {expired_product.name} решил стать новым видом "
            f"сыра с плесенью!"
        )
        assert result == expected, "Неверное сообщение о просроченном продукте"


def test_suggest_shopping_items(db_session, test_user):
    """Тест функции предложения покупок."""
    # создаем дополнительные продукты для анализа частоты
    for i in range(3):
        product = Product(
            name="Хлеб",
            category="Выпечка",
            quantity=1.0,
            unit="шт",
            expiry_date=datetime.now(timezone.utc) + timedelta(days=2),
            user_id=test_user.id,
        )
        db_session.add(product)

    for i in range(2):
        product = Product(
            name="Молоко",
            category="Молочные продукты",
            quantity=1.0,
            unit="л",
            expiry_date=datetime.now(timezone.utc) + timedelta(days=4),
            user_id=test_user.id,
        )
        db_session.add(product)

    db_session.commit()

    suggestions = suggest_shopping_items(test_user.id, db, Product)

    # проверяем, что предложения соответствуют частоте
    assert len(suggestions) > 0, "Должны быть предложения покупок"

    # ищем хлеб в предложениях
    bread_suggestion = next(
        (s for s in suggestions if s["name"] == "Хлеб"), None
    )
    assert bread_suggestion is not None, "Хлеб должен быть в предложениях"
    assert bread_suggestion["frequency"] == 3, "Неверная частота для хлеба"
    assert (
        bread_suggestion["category"] == "Выпечка"
    ), "Неверная категория для хлеба"
