from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from datetime import datetime
from app import db
from app.models import Product, ShoppingItem
from app.utils import (
    get_expiring_products,
    get_recipe_suggestions,
    get_expired_message,
    suggest_shopping_items,
)
from flask_login import login_required, current_user
from prometheus_client import Counter, Gauge
from app import metrics

# Определяем кастомные метрики для бизнес-логики
products_added = Counter('products_added_total', 'Total number of products added')
products_deleted = Counter('products_deleted_total', 'Total number of products deleted')
products_expiring_soon = Gauge('products_expiring_soon', 'Number of products expiring soon')
products_expired = Gauge('products_expired', 'Number of products that have expired')
products_by_category = Gauge('products_by_category', 'Number of products by category', ['category'])
shopping_items_added = Counter('shopping_items_added_total', 'Total number of shopping items added')
shopping_items_purchased = Counter('shopping_items_purchased_total', 'Total number of shopping items marked as purchased')

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    # Получаем строку поиска из аргументов запроса
    search_query = request.args.get("q", "")

    # Базовый запрос для продуктов текущего пользователя
    query = Product.query.filter_by(user_id=current_user.id)

    # Если есть поисковый запрос, применяем фильтр по имени
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))

    # Получаем отфильтрованный список продуктов
    products = query.all()

    # Остальная логика остается прежней
    expired_products = [p for p in products if p.is_expired()]
    expiring_soon = get_expiring_products(products, days=3)
    suggestions = get_recipe_suggestions(products)
    veterans = sorted(
        products, key=lambda x: x.days_in_fridge(), reverse=True
    )[:5]

    # Обновляем метрики
    products_expiring_soon.set(len(expiring_soon))
    products_expired.set(len(expired_products))
    
    # Обновляем метрику для категорий (сначала сбрасываем старые данные)
    category_counts = {}
    for product in products:
        if product.category not in category_counts:
            category_counts[product.category] = 0
        category_counts[product.category] += 1
    
    for category, count in category_counts.items():
        products_by_category.labels(category=category).set(count)

    return render_template(
        "index.html",
        products=products,
        expired_products=expired_products,
        expiring_soon=expiring_soon,
        suggestions=suggestions,
        veterans=veterans,
        get_expired_message=get_expired_message,
        search_query=search_query,  # Передаем строку поиска в шаблон
    )


@main.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]
        expiry_date = datetime.strptime(
            request.form["expiry_date"], "%Y-%m-%d"
        )

        product = Product(
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date,
            user_id=current_user.id,
        )

        db.session.add(product)
        db.session.commit()

        # Увеличиваем счетчик добавленных продуктов
        products_added.inc()

        flash(f"Продукт {name} успешно добавлен!", "success")
        return redirect(url_for("main.index"))

    return render_template("add_product.html")


@main.route("/edit_product/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.category = request.form["category"]
        product.quantity = float(request.form["quantity"])
        product.unit = request.form["unit"]
        product.expiry_date = datetime.strptime(
            request.form["expiry_date"], "%Y-%m-%d"
        )

        db.session.commit()

        flash(f"Продукт {product.name} обновлен!", "success")
        return redirect(url_for("main.index"))

    return render_template("edit_product.html", product=product)


@main.route("/delete_product/<int:id>")
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    # Увеличиваем счетчик удаленных продуктов
    products_deleted.inc()

    flash(f"Продукт {product.name} удален!", "success")
    return redirect(url_for("main.index"))


@main.route("/statistics")
@login_required
def statistics():
    products = Product.query.filter_by(user_id=current_user.id).all()
    longest_living = sorted(
        products, key=lambda x: x.days_in_fridge(), reverse=True
    )
    categories = {}

    for product in products:
        if product.category in categories:
            categories[product.category] += 1
        else:
            categories[product.category] = 1

    return render_template(
        "statistics.html", longest_living=longest_living, categories=categories
    )


@main.route("/shopping_list")
@login_required
def shopping_list():
    # Получаем все элементы списка покупок пользователя
    items = (
        ShoppingItem.query.filter_by(user_id=current_user.id)
        .order_by(ShoppingItem.priority, ShoppingItem.is_purchased)
        .all()
    )

    # Получаем категории продуктов для выпадающего списка
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]

    # Получаем предложения продуктов на основе истории пользователя
    suggestions = suggest_shopping_items(current_user.id, db, Product)

    return render_template(
        "shopping_list.html",
        items=items,
        categories=categories,
        suggestions=suggestions,
    )


@main.route("/add_shopping_item", methods=["POST"])
@login_required
def add_shopping_item():
    name = request.form["name"]
    category = request.form.get("category", "")
    quantity = request.form.get("quantity", "")
    unit = request.form.get("unit", "")
    priority = int(request.form.get("priority", 2))

    # Проверяем правильность ввода количества
    if quantity:
        try:
            quantity = float(quantity)
        except ValueError:
            quantity = None
    else:
        quantity = None

    # Создаем новый элемент списка покупок
    item = ShoppingItem(
        name=name,
        category=category,
        quantity=quantity,
        unit=unit,
        priority=priority,
        user_id=current_user.id,
    )

    db.session.add(item)
    db.session.commit()

    # Увеличиваем счетчик добавленных элементов списка покупок
    shopping_items_added.inc()

    flash(f"Продукт '{name}' добавлен в список покупок", "success")
    return redirect(url_for("main.shopping_list"))


@main.route("/delete_shopping_item/<int:id>")
@login_required
def delete_shopping_item(id):
    item = ShoppingItem.query.get_or_404(id)

    # Проверяем, принадлежит ли элемент текущему пользователю
    if item.user_id != current_user.id:
        flash("У вас нет прав на удаление этого элемента", "danger")
        return redirect(url_for("main.shopping_list"))

    db.session.delete(item)
    db.session.commit()

    flash(f"Продукт '{item.name}' удален из списка покупок", "success")
    return redirect(url_for("main.shopping_list"))


@main.route("/toggle_shopping_item/<int:id>", methods=["POST"])
@login_required
def toggle_shopping_item(id):
    item = ShoppingItem.query.get_or_404(id)

    # Проверяем, принадлежит ли элемент текущему пользователю
    if item.user_id != current_user.id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False}), 403
        flash("У вас нет прав на изменение этого элемента", "danger")
        return redirect(url_for("main.shopping_list"))

    # Меняем статус покупки на противоположный
    was_purchased = item.is_purchased
    item.is_purchased = not was_purchased
    db.session.commit()

    # Если элемент был отмечен как приобретенный, увеличиваем счетчик
    if not was_purchased and item.is_purchased:
        shopping_items_purchased.inc()

    # Если это AJAX запрос, возвращаем JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "is_purchased": item.is_purchased})

    return redirect(url_for("main.shopping_list"))


@main.route("/generate_shopping_list")
@login_required
def generate_shopping_list():
    # Получаем все продукты, которые скоро закончатся (менее 2 единиц)
    low_stock_products = Product.query.filter(
        Product.user_id == current_user.id, Product.quantity < 2
    ).all()

    # Получаем все текущие элементы списка покупок
    current_items = ShoppingItem.query.filter_by(
        user_id=current_user.id, is_purchased=False
    ).all()
    current_item_names = [item.name.lower() for item in current_items]

    added_count = 0
    for product in low_stock_products:
        if product.name.lower() not in current_item_names:
            item = ShoppingItem(
                name=product.name,
                category=product.category,
                unit=product.unit,
                priority=1,  # Высокий приоритет для заканчивающихся продуктов
                user_id=current_user.id,
            )
            db.session.add(item)
            added_count += 1
            shopping_items_added.inc()

    db.session.commit()

    if added_count > 0:
        flash(
            f"Автоматически добавлено {added_count} продуктов в список покупок",  # noqa: E501
            "success",
        )
    else:
        flash(
            "Нет продуктов для автоматического добавления", "info"
        )  # noqa: E501

    return redirect(url_for("main.shopping_list"))
