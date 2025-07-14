# app/blueprints/users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from ..models import Usuario, db

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/list')
def list_users():
    """Lista todos os usuários cadastrados"""
    usuarios = Usuario.query.all()
    return render_template('users/list.html', usuarios=usuarios, usuario=current_user)

@users_bp.route('/profile/<int:user_id>')
def profile(user_id):
    """Exibe o perfil de um usuário específico"""
    usuario = Usuario.query.get_or_404(user_id)
    return render_template('users/profile.html', usuario=usuario)

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edita os dados de um usuário"""
    usuario = Usuario.query.get_or_404(user_id)
    
    # Verifica se o usuário pode editar este perfil (apenas o próprio usuário)
    if current_user.id != user_id:
        flash('Você não tem permissão para editar este perfil.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.biografia = request.form.get('biografia')
        nova_senha = request.form.get('senha')

        if nova_senha:
            usuario.senha = nova_senha  # setter do hash

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('users.profile', user_id=user_id))

    return render_template('users/edit.html', usuario=usuario)

@users_bp.route('/delete', methods=['POST'])
@login_required
def delete_user():
    """Deleta a conta do usuário atual"""
    try:
        usuario = current_user  # Salva o usuário atual
        logout_user()  # Desloga primeiro
        db.session.delete(usuario)  # Depois de deslogar, deleta
        db.session.commit()
        flash('Usuário deletado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar usuário: {str(e)}', 'danger')
        return redirect(url_for('main.index'))