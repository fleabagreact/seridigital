# app/blueprints/posts.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/')
def list_posts():
    """Lista todos os posts"""
    # TODO: Implementar listagem de posts
    return render_template('posts/list.html')

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Cria um novo post"""
    if request.method == 'POST':
        # TODO: Implementar criação de posts
        flash('Funcionalidade de posts será implementada em breve!', 'info')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('posts/create.html')

@posts_bp.route('/<int:post_id>')
def view_post(post_id):
    """Visualiza um post específico"""
    # TODO: Implementar visualização de post
    return render_template('posts/view.html', post_id=post_id)

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edita um post"""
    # TODO: Implementar edição de posts
    if request.method == 'POST':
        flash('Funcionalidade de edição de posts será implementada em breve!', 'info')
        return redirect(url_for('posts.view_post', post_id=post_id))
    
    return render_template('posts/edit.html', post_id=post_id)

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Deleta um post"""
    # TODO: Implementar deleção de posts
    flash('Funcionalidade de deleção de posts será implementada em breve!', 'info')
    return redirect(url_for('posts.list_posts'))