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

    # blueprints
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.users import users_bp
    from .blueprints.posts import posts_bp
    from .blueprints.content import content_bp
    from .blueprints.redirects import redirects_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(redirects_bp)

    return app
