from flask import Flask, render_template, url_for, request, redirect, flash
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'chave_secreta'

engine = create_engine("sqlite:///meubanco.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String)
    email = Column(String)
    senha = Column(String)
    biografia = Column(String)

    def __init__(self, nome, email, senha, biografia):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.biografia = biografia

Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cad_users', methods=['GET', 'POST'])
def cad_user():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        biografia = request.form['biografia']

        novo_usuario = Usuario(nome, email, senha, biografia)
        session.add(novo_usuario)
        session.commit()
        flash('Usuário cadastrado com sucesso!')
        return redirect('/')

    return render_template('cad_users.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
