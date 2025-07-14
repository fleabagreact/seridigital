# app/blueprints/redirects.py
# Blueprint para manter compatibilidade com URLs antigas
from flask import Blueprint, redirect, url_for

redirects_bp = Blueprint('redirects', __name__)

@redirects_bp.route('/cad_users')
def old_register():
    """Redireciona URL antiga de cadastro para nova"""
    return redirect(url_for('auth.register'), code=301)

@redirects_bp.route('/lista_users')
def old_list_users():
    """Redireciona URL antiga de listagem para nova"""
    return redirect(url_for('users.list_users'), code=301)

@redirects_bp.route('/atualizar_usuario/<int:user_id>')
def old_update_user(user_id):
    """Redireciona URL antiga de atualização para nova"""
    return redirect(url_for('users.edit_user', user_id=user_id), code=301)