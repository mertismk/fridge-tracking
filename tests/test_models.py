"""
Юнит-тесты для моделей приложения.
Тестируют функциональность моделей данных, их методы и взаимодействие с базой данных.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models import User, Product, ShoppingItem
from sqlalchemy.exc import IntegrityError


def test_user_model(db_session):
    """Тест модели пользователя."""
    # Создаем пользователя
    user = User(username="testuser", email="test@example.com")
    user.set_password("test_password")
    db_session.add(user)
    db_session.commit()
    
    # Проверяем, что пользователь создан корректно
    assert user.id is not None, "ID пользователя не должен быть None"
    assert user.username == "testuser", "Имя пользователя должно совпадать с заданным"
    assert user.email == "test@example.com", "Email должен совпадать с заданным"
    assert user.check_password("test_password"), "Пароль должен быть корректно установлен"
    assert not user.check_password("wrong_password"), "Проверка неверного пароля должна возвращать False"
    
    # Проверяем метод __repr__
    assert "User" in str(user), "__repr__ должен содержать класс"
    assert "testuser" in str(user), "__repr__ должен содержать имя пользователя"


def test_user_unique_constraints(db_session):
    """Тест уникальности имени пользователя и email."""
    # Создаем первого пользователя
    user1 = User(username="unique_user", email="unique@example.com")
    user1.set_password("password")
    db_session.add(user1)
    db_session.commit()
    
    # Пытаемся создать пользователя с тем же именем
    user2 = User(username="unique_user", email="another@example.com")
    user2.set_password("password")
    db_session.add(user2)
    
    # Должно возникнуть исключение
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    # Откатываем транзакцию
    db_session.rollback()
    
    # Пытаемся создать пользователя с тем же email
    user3 = User(username="another_user", email="unique@example.com")
    user3.set_password("password")
    db_session.add(user3)
    
    # Снова должно возникнуть исключение
    with pytest.raises(IntegrityError):
        db_session.commit()
    
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
    assert abs((product.expiry_date - expiry_date).total_seconds()) < 1, "Срок годности должен совпадать с заданным"
    assert product.user_id == user.id, "ID пользователя должен совпадать с заданным"
    
    # Проверяем метод is_expired
    assert not product.is_expired(), "Новый продукт не должен быть просроченным"
    
    # Проверяем метод days_until_expiry
    assert 4 <= product.days_until_expiry() <= 5, "Срок до истечения должен быть около 5 дней"
    
    # Проверяем метод __repr__
    assert "Product" in str(product), "__repr__ должен содержать класс"
    assert "Тестовый продукт" in str(product), "__repr__ должен содержать название продукта"


def test_product_expiry(db_session):
    """Тест функциональности определения срока годности продукта."""
    # Создаем пользователя
    user = User(username="expiry_test_user", email="expiry_test@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    # Текущее время для тестов
    now = datetime.now(timezone.utc)
    
    # Продукт с прошедшим сроком годности
    expired_product = Product(
        name="Просроченный продукт",
        category="Тестовая категория",
        quantity=1.0,
        unit="шт",
        expiry_date=now - timedelta(days=1),
        user_id=user.id
    )
    
    # Продукт с будущим сроком годности
    future_product = Product(
        name="Свежий продукт",
        category="Тестовая категория",
        quantity=1.0,
        unit="шт",
        expiry_date=now + timedelta(days=10),
        user_id=user.id
    )
    
    db_session.add_all([expired_product, future_product])
    db_session.commit()
    
    # Проверяем методы для просроченного продукта
    assert expired_product.is_expired(), "Продукт с прошедшей датой должен быть просроченным"
    assert expired_product.days_until_expiry() < 0, "Дней до истечения срока должно быть отрицательное число"
    
    # Проверяем методы для свежего продукта
    assert not future_product.is_expired(), "Продукт с будущей датой не должен быть просроченным"
    assert 9 <= future_product.days_until_expiry() <= 10, "Дней до истечения срока должно быть около 10"


def test_shopping_item_model(db_session):
    """Тест модели списка покупок."""
    # Создаем пользователя
    user = User(username="shopping_test_user", email="shopping_test@example.com")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    # Создаем элемент списка покупок
    item = ShoppingItem(
        name="Тестовый товар",
        quantity=2.0,
        unit="шт",
        user_id=user.id
    )
    db_session.add(item)
    db_session.commit()
    
    # Проверяем, что элемент создан корректно
    assert item.id is not None, "ID элемента не должен быть None"
    assert item.name == "Тестовый товар", "Название товара должно совпадать с заданным"
    assert item.quantity == 2.0, "Количество должно совпадать с заданным"
    assert item.unit == "шт", "Единица измерения должна совпадать с заданной"
    assert item.user_id == user.id, "ID пользователя должен совпадать с заданным"
    assert item.priority == 2, "Приоритет по умолчанию должен быть 2"
    assert not item.is_purchased, "По умолчанию товар не должен быть куплен"
    
    # Проверяем метод __repr__
    assert "ShoppingItem" in str(item), "__repr__ должен содержать класс"
    assert "Тестовый товар" in str(item), "__repr__ должен содержать название товара"
