from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User", backref=db.backref("products", lazy=True))

    from datetime import datetime, timezone

    def is_expired(self):
        return datetime.now(timezone.utc) > self.expiry_date.astimezone(timezone.utc)

    def days_until_expiry(self):
        now = datetime.now(timezone.utc)
        expiry_date = self.expiry_date.astimezone(timezone.utc)

        if self.is_expired():
            return -((now - expiry_date).days)
        return (expiry_date - now).days

    def days_in_fridge(self):
        return (
            datetime.now(timezone.utc) - self.date_added.astimezone(timezone.utc)
        ).days

    def get_rank(self):
        days = self.days_in_fridge()
        if days > 30:
            return "Ветеран холодильника"
        elif days > 20:
            return "Опытный обитатель"
        elif days > 10:
            return "Постоялец"
        elif days > 5:
            return "Новосёл"
        else:
            return "Новобранец"

    def __repr__(self):
        return f"<Product {self.name}>"


class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    priority = db.Column(db.Integer, default=2)  # 1 - высокий, 2 - средний, 3 - низкий
    is_purchased = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("shopping_items", lazy=True))

    def __repr__(self):
        return f"<ShoppingItem {self.name}>"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
