# app/blueprints/content.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Content, db

content_bp = Blueprint('content', __name__, url_prefix='/content')

@content_bp.route('/')
def list_content():
    """Lista todo o conteúdo disponível"""
    contents = Content.query.all()
    return render_template('content/list.html', contents=contents)

@content_bp.route('/<int:content_id>')
def view_content(content_id):
    """Visualiza um conteúdo específico"""
    content = Content.query.get_or_404(content_id)
    return render_template('content/view.html', content=content)

@content_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_content():
    """Cria novo conteúdo"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content_type = request.form.get('type')
        url = request.form.get('url')
        thumbnail = request.form.get('thumbnail')
        release_date = request.form.get('release_date')
        
        # Converte a data se fornecida
        from ..utils.helpers import parse_date
        release_date_obj = parse_date(release_date)
        if release_date and not release_date_obj:
            return render_template('content/create.html')
        
        new_content = Content(
            title=title,
            description=description,
            type=content_type,
            url=url,
            thumbnail=thumbnail,
            release_date=release_date_obj
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        flash('Conteúdo criado com sucesso!', 'success')
        return redirect(url_for('content.list_content'))
    
    return render_template('content/create.html')

@content_bp.route('/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_content(content_id):
    """Edita um conteúdo"""
    content = Content.query.get_or_404(content_id)
    
    if request.method == 'POST':
        content.title = request.form.get('title')
        content.description = request.form.get('description')
        content.type = request.form.get('type')
        content.url = request.form.get('url')
        content.thumbnail = request.form.get('thumbnail')
        
        # Atualizar data de lançamento se fornecida
        release_date = request.form.get('release_date')
        if release_date:
            from ..utils.helpers import parse_date
            content.release_date = parse_date(release_date)
        
        db.session.commit()
        flash('Conteúdo atualizado com sucesso!', 'success')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    return render_template('content/edit.html', content=content)

@content_bp.route('/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_content(content_id):
    """Deleta um conteúdo"""
    content = Content.query.get_or_404(content_id)
    
    try:
        db.session.delete(content)
        db.session.commit()
        flash('Conteúdo deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar conteúdo: {str(e)}', 'danger')
    
    return redirect(url_for('content.list_content'))