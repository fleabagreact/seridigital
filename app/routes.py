from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import check_password_hash
from .models import Usuario, db
from .extensions import login_manager

bp = Blueprint('bp', __name__)

@bp.route('/')
def index():
    return render_template('index.html', usuario=current_user)

@bp.route('/cad_users', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('bp.index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        biografia = request.form.get('biografia')

        # Verifica se já existe usuário com este email
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'warning')
            return redirect(url_for('bp.register'))

        # Cria e salva novo usuário
        novo = Usuario(nome=nome, email=email, biografia=biografia)
        novo.senha = senha  # setter já faz hash
        db.session.add(novo)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Você já pode logar.', 'success')
        return redirect(url_for('bp.login'))

    # GET
    return render_template('cad_users.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bp.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()

        if not email or not senha:
            flash('E-mail e senha são obrigatórios.', 'warning')
            return redirect(url_for('bp.login'))

        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            next_page = request.args.get('next') or url_for('bp.index')
            return redirect(next_page)
        else:
            flash('E-mail ou senha incorretos.', 'danger')
            return redirect(url_for('bp.login'))

    # GET
    return render_template('login.html')

#Listar usuários cadastrados

@bp.route('/lista_users')
def lista_users():
    usuarios = Usuario.query.all()
    return render_template('lista_users.html', usuarios=usuarios, usuario=current_user)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('bp.index'))

# Função para o Flask-Login recarregar o usuário a partir do ID salvo na sessão
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rota para exibir o formulário e processar a atualização dos dados de um usuário existente
@bp.route('/atualizar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.biografia = request.form.get('biografia')
        nova_senha = request.form.get('senha')

        if nova_senha:
            usuario.senha = nova_senha  # setter do hash

        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('bp.index'))

    return render_template('atualizar_usuario.html', usuario=usuario)

@bp.route('/deletar_usuario', methods=['POST'])
@login_required
def deletar_usuario():
    try:
        usuario = current_user  # Salva o usuário atual
        logout_user()  # Desloga primeiro
        db.session.delete(usuario)  # Depois de deslogar, deleta
        db.session.commit()
        flash('Usuário deletado com sucesso!', 'success')
        return redirect(url_for('bp.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar usuário: {str(e)}', 'danger')
        return redirect(url_for('bp.index'))
