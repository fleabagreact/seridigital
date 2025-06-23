

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = (
        db.UniqueConstraint('email', name='uq_usuario_email'),
        {'sqlite_autoincrement': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    _senha_hash = db.Column('senha', db.String(128), nullable=False)
    biografia = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Usuario {self.email}>"

    @property
    def senha(self):
        raise AttributeError("Senha não pode ser lida diretamente.")

    @senha.setter
    def senha(self, senha_plaintext):
        self._senha_hash = generate_password_hash(senha_plaintext)

    def checar_senha(self, senha_plaintext):
        return check_password_hash(self._senha_hash, senha_plaintext)
