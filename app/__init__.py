# app/__init__.py
from flask import Flask
from flask_migrate import Migrate
from .config import BaseConfig
from .models import db
from .extensions import login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    # database
    db.init_app(app)
    Migrate(app, db)

    # login
    login_manager.init_app(app)

    # routes
    from .routes import bp
    app.register_blueprint(bp)

    return app
