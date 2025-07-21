from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'tb_users'
    __table_args__ = (
        db.UniqueConstraint('usr_email', name='uq_usuario_email'),
        {'sqlite_autoincrement': True}
    )

    id = db.Column('usr_id', db.Integer, primary_key=True)
    nome = db.Column('usr_name', db.String(255), nullable=False)
    email = db.Column('usr_email', db.String(255), nullable=False, unique=True, index=True)
    _senha_hash = db.Column('usr_password', db.String(255), nullable=False)
    profile_picture = db.Column('usr_profile_picture', db.String(255))
    biografia = db.Column('usr_bio', db.Text)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    criado_em = db.Column('usr_created_at', db.DateTime, default=datetime.utcnow, nullable=False)


    # Relacionamentos
    seguidores = db.relationship('Follower', foreign_keys='Follower.follower_id', backref='seguidor', lazy='dynamic')
    seguidos = db.relationship('Follower', foreign_keys='Follower.followed_id', backref='seguido', lazy='dynamic')
    mensagens_enviadas = db.relationship('PrivateMessage', foreign_keys='PrivateMessage.sender_id', backref='sender', lazy='dynamic')
    mensagens_recebidas = db.relationship('PrivateMessage', foreign_keys='PrivateMessage.receiver_id', backref='receiver', lazy='dynamic')
    comentarios = db.relationship('Comment', backref='user', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    historico_assistido = db.relationship('WatchHistory', backref='user', lazy='dynamic')
    avaliacoes = db.relationship('Rating', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"<Usuario {self.email}>"


    def is_administrador(self):
        return self.is_admin

    @property
    def senha(self):
        raise AttributeError("Senha não pode ser lida diretamente.")

    @senha.setter
    def senha(self, senha_plaintext):
        self._senha_hash = generate_password_hash(senha_plaintext)

    def checar_senha(self, senha_plaintext):
        return check_password_hash(self._senha_hash, senha_plaintext)
    
    

class Follower(db.Model):
    __tablename__ = 'tb_followers'

    follower_id = db.Column('fol_follower_id', db.Integer, db.ForeignKey('tb_users.usr_id'), primary_key=True)
    followed_id = db.Column('fol_followed_id', db.Integer, db.ForeignKey('tb_users.usr_id'), primary_key=True)
    followed_at = db.Column('fol_followed_at', db.DateTime, default=datetime.utcnow, nullable=False)

class PrivateMessage(db.Model):
    __tablename__ = 'tb_private_messages'

    id = db.Column('msg_id', db.Integer, primary_key=True)
    sender_id = db.Column('msg_sender_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    receiver_id = db.Column('msg_receiver_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    text = db.Column('msg_text', db.Text, nullable=False)
    sent_at = db.Column('msg_sent_at', db.DateTime, default=datetime.utcnow, nullable=False)
    is_read = db.Column('msg_is_read', db.Boolean, default=False, nullable=False)

#Classe para que as mensagens fiquem visiveis para todos os usuários
class CommunityPost(db.Model):
    __tablename__ = 'tb_community_posts'

    id = db.Column('post_id', db.Integer, primary_key=True)
    author_id = db.Column('post_author_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    content = db.Column('post_content', db.Text, nullable=False)
    created_at = db.Column('post_created_at', db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', backref='community_posts')


class Comment(db.Model):
    __tablename__ = 'tb_comments'

    id = db.Column('cmt_id', db.Integer, primary_key=True)
    user_id = db.Column('cmt_user_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    content_id = db.Column('cmt_content_id', db.Integer, db.ForeignKey('tb_contents.cnt_id'), nullable=False)
    text = db.Column('cmt_text', db.Text, nullable=False)
    created_at = db.Column('cmt_created_at', db.DateTime, default=datetime.utcnow, nullable=False)

class Like(db.Model):
    __tablename__ = 'tb_likes'

    id = db.Column('lik_id', db.Integer, primary_key=True)
    user_id = db.Column('lik_user_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    content_id = db.Column('lik_content_id', db.Integer, db.ForeignKey('tb_contents.cnt_id'), nullable=False)
    created_at = db.Column('lik_created_at', db.DateTime, default=datetime.utcnow, nullable=False)

class WatchHistory(db.Model):
    __tablename__ = 'tb_watch_history'

    id = db.Column('wht_id', db.Integer, primary_key=True)
    user_id = db.Column('wht_user_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    content_id = db.Column('wht_content_id', db.Integer, db.ForeignKey('tb_contents.cnt_id'), nullable=False)
    last_watched = db.Column('wht_last_watched', db.DateTime, default=datetime.utcnow, nullable=False)
    progress = db.Column('wht_progress', db.Float, nullable=False)

class Rating(db.Model):
    __tablename__ = 'tb_ratings'

    id = db.Column('rat_id', db.Integer, primary_key=True)
    user_id = db.Column('rat_user_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    content_id = db.Column('rat_content_id', db.Integer, db.ForeignKey('tb_contents.cnt_id'), nullable=False)
    rating = db.Column('rat_rating', db.Integer, nullable=False)
    created_at = db.Column('rat_created_at', db.DateTime, default=datetime.utcnow, nullable=False)

class Content(db.Model):
    __tablename__ = 'tb_contents'

    id = db.Column('cnt_id', db.Integer, primary_key=True)
    title = db.Column('cnt_title', db.String(255), nullable=False)
    description = db.Column('cnt_description', db.Text)
    type = db.Column('cnt_type', db.String(50), nullable=False)  # ENUM substituído por String devido à falta de valores
    release_date = db.Column('cnt_release_date', db.Date)
    thumbnail = db.Column('cnt_thumbnail', db.String(255))
    url = db.Column('cnt_url', db.String(255))
    created_at = db.Column('cnt_created_at', db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    comentarios = db.relationship('Comment', backref='content', lazy='dynamic')
    likes = db.relationship('Like', backref='content', lazy='dynamic')
    historico_assistido = db.relationship('WatchHistory', backref='content', lazy='dynamic')
    avaliacoes = db.relationship('Rating', backref='content', lazy='dynamic')
    categorias = db.relationship('ContentCategory', backref='content', lazy='dynamic')

class Category(db.Model):
    __tablename__ = 'tb_categories'

    id = db.Column('cat_id', db.Integer, primary_key=True)
    name = db.Column('cat_name', db.String(255), nullable=False)

    # Relacionamento
    conteudos = db.relationship('ContentCategory', backref='category', lazy='dynamic')

class ContentCategory(db.Model):
    __tablename__ = 'tb_content_categories'

    content_id = db.Column('cct_content_id', db.Integer, db.ForeignKey('tb_contents.cnt_id'), primary_key=True)
    category_id = db.Column('cct_category_id', db.Integer, db.ForeignKey('tb_categories.cat_id'), primary_key=True)