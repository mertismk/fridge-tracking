"""
Юнит-тесты для функций из модуля utils.py.
Тестируют утилиты для работы с продуктами и рекомендациями.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app import create_app, db
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
    """Создает тестового пользователя."""
    user = User(username="testutil", email="testutil@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_products(db_session, test_user):
    """Создает набор тестовых продуктов."""
    now = datetime.now(timezone.utc)
    
    # Продукт, который испортится через 2 дня
    expiring_soon = Product(
        name="Скоро испортится",
        category="Овощи",
        quantity=1.0,
        unit="кг",
        expiry_date=now + timedelta(days=2),
        user_id=test_user.id
    )
    
    # Продукт, который испортится через 5 дней
    expiring_later = Product(
        name="Испортится нескоро",
        category="Мясо",
        quantity=0.5,
        unit="кг",
        expiry_date=now + timedelta(days=5),
        user_id=test_user.id
    )
    
    # Продукт, который уже испортился
    expired = Product(
        name="Уже испортился",
        category="Молочные продукты",
        quantity=0.5,
        unit="л",
        expiry_date=now - timedelta(days=1),
        user_id=test_user.id
    )
    
    # Продукт - фрукт для тестов рецептов
    fruit = Product(
        name="Банан",
        category="Фрукты",
        quantity=3.0,
        unit="шт",
        expiry_date=now + timedelta(days=4),
        user_id=test_user.id
    )
    
    db_session.add_all([expiring_soon, expiring_later, expired, fruit])
    db_session.commit()
    
    return {
        'expiring_soon': expiring_soon,
        'expiring_later': expiring_later,
        'expired': expired,
        'fruit': fruit,
        'all': [expiring_soon, expiring_later, expired, fruit]
    }


def test_get_expiring_products(test_products):
    """Тест функции получения продуктов с истекающим сроком годности."""
    # Проверяем с дефолтным значением days=3
    expiring = get_expiring_products(test_products['all'])
    # Проверяем, что в результатах только продукты, которые истекают в течение 3 дней
    assert len(expiring) == 1, "Должен быть только один продукт с истекающим сроком годности (до 3 дней)"
    assert expiring[0].name == "Скоро испортится", "Неверный продукт в списке истекающих"
    
    # Проверяем с увеличенным значением days=6
    expiring_more = get_expiring_products(test_products['all'], days=6)
    assert len(expiring_more) == 3, "Должно быть три продукта с истекающим сроком годности (до 6 дней)"
    names = [p.name for p in expiring_more]
    assert "Скоро испортится" in names, "Отсутствует ожидаемый продукт в списке истекающих"
    assert "Испортится нескоро" in names, "Отсутствует ожидаемый продукт в списке истекающих"
    assert "Банан" in names, "Отсутствует ожидаемый продукт в списке истекающих"


def test_get_recipe_suggestions(test_products):
    """Тест функции получения рекомендаций рецептов."""
    # Проверяем рекомендации по нашему набору продуктов
    suggestions = get_recipe_suggestions(test_products['all'])
    
    # Должно быть предложение "Мясо с овощами", т.к. есть категории "Мясо" и "Овощи"
    assert len(suggestions) >= 1, "Должно быть как минимум одно предложение рецепта"
    
    # Ищем рецепт "Мясо с овощами"
    meat_recipe = next((s for s in suggestions if s["name"] == "Мясо с овощами"), None)
    assert meat_recipe is not None, "Должен быть рецепт 'Мясо с овощами'"
    
    # Проверяем, что продукты из нужных категорий включены в рецепт
    products_in_recipe = meat_recipe["products"]
    assert "Скоро испортится" in products_in_recipe, "Продукт из категории 'Овощи' не включен в рецепт"
    assert "Испортится нескоро" in products_in_recipe, "Продукт из категории 'Мясо' не включен в рецепт"
    
    # Проверяем, что просроченный продукт не включен в рецепт
    assert "Уже испортился" not in products_in_recipe, "Просроченный продукт не должен быть в рецепте"


def test_get_expired_message(test_products):
    """Тест функции получения сообщения для просроченного продукта."""
    # Патчим random.choice для предсказуемого результата
    with patch('random.choice', return_value="Кажется, {product.name} решил стать новым видом сыра с плесенью!"):
        message = get_expired_message(test_products['expired'])
        expected = "Кажется, Уже испортился решил стать новым видом сыра с плесенью!"
        assert message == expected, "Неверное сообщение о просроченном продукте"


def test_suggest_shopping_items(db_session, test_user):
    """Тест функции предложения покупок."""
    # Создаем дополнительные продукты для анализа частоты
    for i in range(3):
        product = Product(
            name="Хлеб",
            category="Выпечка",
            quantity=1.0,
            unit="шт",
            expiry_date=datetime.now(timezone.utc) + timedelta(days=2),
            user_id=test_user.id
        )
        db_session.add(product)
    
    for i in range(2):
        product = Product(
            name="Молоко",
            category="Молочные продукты",
            quantity=1.0,
            unit="л",
            expiry_date=datetime.now(timezone.utc) + timedelta(days=4),
            user_id=test_user.id
        )
        db_session.add(product)
    
    db_session.commit()
    
    # Получаем предложения покупок
    suggestions = suggest_shopping_items(test_user.id, db, Product)
    
    # Проверяем, что предложения соответствуют частоте
    assert len(suggestions) > 0, "Должны быть предложения покупок"
    
    # Ищем хлеб в предложениях
    bread_suggestion = next((s for s in suggestions if s["name"] == "Хлеб"), None)
    assert bread_suggestion is not None, "Хлеб должен быть в предложениях"
    assert bread_suggestion["frequency"] == 3, "Неверная частота для хлеба"
    assert bread_suggestion["category"] == "Выпечка", "Неверная категория для хлеба"
