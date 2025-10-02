# app/__init__.py
from flask import Flask
import os
from flask_migrate import Migrate
from .config import BaseConfig
from .models import db
from .extensions import login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    # database
    # Garante que a pasta do SQLite exista (ex.: app/database/meubanco.db)
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri.startswith('sqlite:///'):
        db_path = uri.replace('sqlite:///', '', 1)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    db.init_app(app)
    Migrate(app, db)

    # Cria tabelas automaticamente em ambientes sem migração aplicada
    with app.app_context():
        db.create_all()
        
        # Aplicar todas as migrações pendentes
        try:
            from .migrate_on_startup import apply_all_migrations
            apply_all_migrations(db)
        except Exception as e:
            print(f"⚠️  Erro ao aplicar migrações: {e}")
        
        # Criar conta e comunidade padrão SeriDigital
        try:
            from .init_default_data import create_default_account_and_community
            create_default_account_and_community()
        except Exception as e:
            print(f"⚠️  Erro ao criar dados padrão: {e}")

    # login
    login_manager.init_app(app)

    # blueprints
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.users import users_bp
    from .blueprints.posts import posts_bp
    from .blueprints.content import content_bp
    from .blueprints.redirects import redirects_bp
    from .blueprints.chat import chat_bp
    from .blueprints.comunidade import comunidade_bp
    from .blueprints.feedbacks import feedback_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(redirects_bp)
    app.register_blueprint(comunidade_bp)

    return app