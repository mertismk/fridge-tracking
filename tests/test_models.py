"""
Юнит-тесты для моделей приложения.
Тестируют функциональность моделей данных, их методы и взаимодействие с базой данных.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models import User, Product, ShoppingItem
from sqlalchemy.exc import IntegrityError
from app import db


def test_user_model(db_session):
    """Тест модели пользователя."""
    # Создаем пользователя
    user = User(username="test_user", email="test_user@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    # Проверяем, что пользователь создан корректно
    assert user.id is not None, "ID пользователя не должен быть None"
    assert user.username == "test_user", "Имя пользователя должно совпадать с заданным"
    assert user.email == "test_user@example.com", "Email должен совпадать с заданным"
    assert user.check_password("password"), "Проверка пароля должна возвращать True"
    assert not user.check_password("wrong_password"), "Проверка неверного пароля должна возвращать False"
    
    # Проверяем метод __repr__
    assert "User" in str(user), "__repr__ должен содержать класс"
    assert "test_user" in str(user), "__repr__ должен содержать имя пользователя"


def test_user_unique_constraints(db_session):
    """Тест уникальности пользователя."""
    # Создаем первого пользователя
    user1 = User(username="user1", email="user1@example.com")
    user1.set_password("password")
    db_session.add(user1)
    db_session.commit()
    
    # Создаем пользователя с тем же именем
    user2 = User(username="user1", email="user2@example.com")
    user2.set_password("password")
    db_session.add(user2)
    
    # Проверяем, что возникает ошибка при коммите
    try:
        db_session.commit()
        assert False, "Должна быть ошибка уникальности для username"
    except:
        db_session.rollback()
    
    # Создаем пользователя с тем же email
    user3 = User(username="user3", email="user1@example.com")
    user3.set_password("password")
    db_session.add(user3)
    
    # Проверяем, что возникает ошибка при коммите
    try:
        db_session.commit()
        assert False, "Должна быть ошибка уникальности для email"
    except:
        db_session.rollback()


def test_product_model(db_session):
    """Тест модели продукта."""
    # Создаем пользователя
    user = User(username="product_test_user", email="product_test@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    # Текущее время для тестов
    now = datetime.now(timezone.utc)
    expiry_date = now + timedelta(days=5)
    
    # Создаем продукт
    product = Product(
        name="Тестовый продукт",
        category="Тестовая категория",
        quantity=1.5,
        unit="кг",
        expiry_date=expiry_date,
        user_id=user.id
    )
    db_session.add(product)
    db_session.commit()
    
    # Проверяем, что продукт создан корректно
    assert product.id is not None, "ID продукта не должен быть None"
    assert product.name == "Тестовый продукт", "Название продукта должно совпадать с заданным"
    assert product.category == "Тестовая категория", "Категория должна совпадать с заданной"
    assert product.quantity == 1.5, "Количество должно совпадать с заданным"
    assert product.unit == "кг", "Единица измерения должна совпадать с заданной"
    
    # Исправляем сравнение дат с учетом timezone
    assert product.expiry_date.astimezone(timezone.utc).date() == expiry_date.date(), "Срок годности должен совпадать с заданным"
    
    # Проверяем метод is_expired
    assert not product.is_expired(), "Новый продукт не должен быть просроченным"
    
    # Проверяем метод days_until_expiry
    assert 4 <= product.days_until_expiry() <= 5, "Срок до истечения должен быть около 5 дней"
    
    # Проверяем метод __repr__
    assert "Product" in str(product), "__repr__ должен содержать класс"
    assert "Тестовый продукт" in str(product), "__repr__ должен содержать название продукта"


def test_product_expiry(db_session):
    """Тест методов проверки срока годности продукта."""
    user = User(username="expiry_test_user", email="expiry_test@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    now = datetime.now(timezone.utc)
    
    # Создаем продукт, который уже просрочен
    expired_product = Product(
        name="Просроченный продукт",
        category="Тест",
        quantity=1.0,
        unit="шт",
        expiry_date=now - timedelta(days=1),
        user_id=user.id
    )
    
    # Создаем продукт, который просрочится через 3 дня
    expiring_soon = Product(
        name="Скоро просрочится",
        category="Тест",
        quantity=1.0,
        unit="шт",
        expiry_date=now + timedelta(days=3),
        user_id=user.id
    )
    
    # Создаем продукт с длительным сроком годности
    fresh_product = Product(
        name="Свежий продукт",
        category="Тест",
        quantity=1.0,
        unit="шт",
        expiry_date=now + timedelta(days=30),
        user_id=user.id
    )
    
    # Сохраняем продукты в БД
    db_session.add_all([expired_product, expiring_soon, fresh_product])
    db_session.commit()
    
    # Проверяем метод is_expired
    assert expired_product.is_expired(), "Просроченный продукт должен определяться как просроченный"
    assert not expiring_soon.is_expired(), "Продукт со сроком годности 3 дня не должен определяться как просроченный"
    assert not fresh_product.is_expired(), "Свежий продукт не должен определяться как просроченный"
    
    # Проверяем метод days_until_expiry
    assert expired_product.days_until_expiry() < 0, "Для просроченного продукта должно возвращаться отрицательное число дней"
    assert 2 <= expiring_soon.days_until_expiry() <= 3, "Для продукта, который просрочится через 3 дня, должно возвращаться примерно 3 дня"
    assert 29 <= fresh_product.days_until_expiry() <= 30, "Для свежего продукта должно возвращаться примерно 30 дней"


def test_shopping_item_model(db_session):
    """Тест модели элемента списка покупок."""
    # Создаем пользователя
    user = User(username="shopping_test_user", email="shopping_test@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    # Создаем элемент списка покупок
    item = ShoppingItem(
        name="Тестовый элемент",
        category="Тестовая категория",
        quantity=2.0,
        unit="шт",
        priority=1,
        is_purchased=False,
        user_id=user.id
    )
    db_session.add(item)
    db_session.commit()
    
    # Проверяем, что элемент создан корректно
    assert item.id is not None, "ID элемента не должен быть None"
    assert item.name == "Тестовый элемент", "Название элемента должно совпадать с заданным"
    assert item.category == "Тестовая категория", "Категория должна совпадать с заданной"
    assert item.quantity == 2.0, "Количество должно совпадать с заданным"
    assert item.unit == "шт", "Единица измерения должна совпадать с заданной"
    assert item.priority == 1, "Приоритет должен совпадать с заданным"
    assert item.is_purchased is False, "Статус покупки должен совпадать с заданным"
    assert item.user_id == user.id, "ID пользователя должен совпадать с заданным"
    
    # Проверяем метод __repr__
    assert "ShoppingItem" in str(item), "__repr__ должен содержать класс"
    assert "Тестовый элемент" in str(item), "__repr__ должен содержать название элемента"
