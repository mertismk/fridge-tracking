from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from app import db
from app.models import Product
from app.utils import get_expiring_products, get_recipe_suggestions, get_expired_message
from flask_login import login_required, current_user

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    products = Product.query.filter_by(user_id=current_user.id).all()
    expired_products = [p for p in products if p.is_expired()]
    expiring_soon = get_expiring_products(products, days=3)
    suggestions = get_recipe_suggestions(products)
    veterans = sorted(products, key=lambda x: x.days_in_fridge(), reverse=True)[:5]

    return render_template(
        "index.html",
        products=products,
        expired_products=expired_products,
        expiring_soon=expiring_soon,
        suggestions=suggestions,
        veterans=veterans,
        get_expired_message=get_expired_message,
    )


@main.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]
        expiry_date = datetime.strptime(request.form["expiry_date"], "%Y-%m-%d")

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
        product.expiry_date = datetime.strptime(request.form["expiry_date"], "%Y-%m-%d")

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

    flash(f"Продукт {product.name} удален!", "success")
    return redirect(url_for("main.index"))


@main.route("/statistics")
@login_required
def statistics():
    products = Product.query.filter_by(user_id=current_user.id).all()
    longest_living = sorted(products, key=lambda x: x.days_in_fridge(), reverse=True)
    categories = {}

    for product in products:
        if product.category in categories:
            categories[product.category] += 1
        else:
            categories[product.category] = 1

    return render_template(
        "statistics.html", longest_living=longest_living, categories=categories
    )
