from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

#cria a instância do banco de dados para poder importar.
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # ajuste o 'bp.login' para o endpoint correto da sua rota de login
