from datetime import datetime, timedelta
import random

def get_expiring_products(products, days=3):
    today = datetime.utcnow()
    soon = today + timedelta(days=days)
    
    return [p for p in products if today < p.expiry_date <= soon]

def get_expired_message(product):
    messages = [
        f"{product.name} уже не первой свежести... Пора прощаться!",
        f"Кажется, {product.name} решил стать новым видом сыра с плесенью!",
        f"У {product.name} закончился контракт с вашим холодильником!",
        f"{product.name} просит политического убежища в мусорном ведре!",
        f"Хьюстон, у нас проблема! {product.name} начал свою собственную экосистему!",
        f"{product.name} теперь официально сертифицирован как биологическое оружие!",
        f"Даже бактерии отказываются жить в {product.name} – слишком тесно!",
        f"На {product.name} уже образовалась своя цивилизация и они требуют независимости!",
        f"Археологи будут в восторге, когда найдут {product.name} через 1000 лет!",
        f"Запах {product.name} заставил соседей вызвать МЧС!",
        f"{product.name} теперь может самостоятельно передвигаться по кухне!",
        f"В темноте {product.name} уже начал светиться и подавать сигналы инопланетянам!",
        f"Поздравляем! {product.name} официально созрел для научных экспериментов!",
        f"{product.name} эволюционировал в новую форму жизни и требует право голоса!",
        f"Если {product.name} выпустить на свободу, он может захватить весь город!"
    ]
    return random.choice(messages)

def get_recipe_suggestions(products):
    valid_products = [p for p in products if not p.is_expired()]
    
    if len(valid_products) < 2:
        return []
    
    suggestions = []
    
    if any(p.category == "Овощи" for p in valid_products) and any(p.category == "Мясо" for p in valid_products):
        suggestions.append({
            "name": "Мясо с овощами",
            "products": [p.name for p in valid_products if p.category in ["Овощи", "Мясо"]][:4],
            "description": "Простое и вкусное блюдо из мяса с овощами."
        })
    
    if any(p.category == "Молочные продукты" for p in valid_products) and any(p.category == "Фрукты" for p in valid_products):
        suggestions.append({
            "name": "Фруктовый смузи",
            "products": [p.name for p in valid_products if p.category in ["Молочные продукты", "Фрукты"]][:3],
            "description": "Освежающий смузи из фруктов и молочных продуктов."
        })
    
    return suggestions

def suggest_shopping_items(user_id, db, Product):
    """
    Предлагает часто добавляемые пользователем продукты для списка покупок
    
    Args:
        user_id: ID пользователя
        db: экземпляр базы данных
        Product: модель Product
        
    Returns:
        list: список словарей с предложениями продуктов
    """
    # Получаем все продукты пользователя с группировкой по названию и подсчетом количества
    product_counts = db.session.query(
        Product.name, 
        Product.category, 
        Product.unit, 
        db.func.count(Product.id).label('count')
    ).filter(
        Product.user_id == user_id
    ).group_by(
        Product.name, 
        Product.category, 
        Product.unit
    ).order_by(
        db.desc('count')
    ).limit(10).all()
    
    # Преобразуем результаты в список словарей
    suggestions = []
    for name, category, unit, count in product_counts:
        suggestions.append({
            "name": name,
            "category": category,
            "unit": unit,
            "frequency": count
        })
    
    return suggestions