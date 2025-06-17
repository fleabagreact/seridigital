from flask import Flask, render_template, url_for, request, redirect, flash
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash  

app = Flask(__name__)
app.secret_key = 'chave_secreta'  

db = create_engine("sqlite:///meubanco.db")
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String)
    senha = Column("senha", String)
    biografia = Column("biografia", String)

    def __init__(self, nome, email, senha, biografia):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.biografia = biografia

Base.metadata.create_all(bind=db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cad_users', methods=['GET', 'POST'])
def cad_users():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        biografia = request.form['biografia']

        if not email:
            flash('Email é obrigatório')
        else:
            senha_hash = generate_password_hash(senha)  # <-- HASH DA SENHA
            usuario = Usuario(nome, email, senha_hash, biografia)
            session.add(usuario)
            session.commit()
            flash('Usuário cadastrado com sucesso!')
            return redirect(url_for('index'))

    return render_template('cad_users.html')
