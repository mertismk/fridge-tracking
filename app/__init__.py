import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from prometheus_flask_exporter import PrometheusMetrics

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_overrides=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Пожалуйста, войдите, чтобы получить доступ к этой странице."
    )
    login_manager.login_message_category = "info"

    if 'prometheus_multiproc_dir' not in os.environ and \
            os.path.exists("./prometheus_metrics_data"):
        os.environ["prometheus_multiproc_dir"] = "./prometheus_metrics_data"
        
    PrometheusMetrics(app)

    from app import routes, auth

    app.register_blueprint(routes.main)
    app.register_blueprint(auth.auth)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    return User.query.get(int(user_id))
