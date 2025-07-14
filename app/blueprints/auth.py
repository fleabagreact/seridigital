# app/blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Usuario, db
from ..extensions import login_manager

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota para cadastro de novos usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        biografia = request.form.get('biografia')

        # Verifica se já existe usuário com este email
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'warning')
            return redirect(url_for('auth.register'))

        # Cria e salva novo usuário
        novo = Usuario(nome=nome, email=email, biografia=biografia)
        novo.senha = senha  # setter já faz hash
        db.session.add(novo)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Você já pode logar.', 'success')
        return redirect(url_for('auth.login'))

    # GET
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()

        if not email or not senha:
            flash('E-mail e senha são obrigatórios.', 'warning')
            return redirect(url_for('auth.login'))

        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            next_page = request.args.get('next') or url_for('main.index')
            return redirect(next_page)
        else:
            flash('E-mail ou senha incorretos.', 'danger')
            return redirect(url_for('auth.login'))

    # GET
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Rota para logout de usuários"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))

# Função para o Flask-Login recarregar o usuário a partir do ID salvo na sessão
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))