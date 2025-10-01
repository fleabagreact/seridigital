# app/blueprints/content.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import Content, db
import os
from werkzeug.utils import secure_filename

content_bp = Blueprint('content', __name__, url_prefix='/content')

@content_bp.route('/')
def list_content():
    """Lista todo o conteúdo disponível"""
    contents = Content.query.all()
    # Passa helpers do YouTube para uso direto nos templates
    from ..utils.helpers import (
        extract_youtube_id,
        youtube_thumbnail_url,
        youtube_embed_url,
    )
    return render_template(
        'content/list.html',
        contents=contents,
        extract_youtube_id=extract_youtube_id,
        youtube_thumbnail_url=youtube_thumbnail_url,
        youtube_embed_url=youtube_embed_url,
    )


@content_bp.route('/buscar', methods=['GET'])
@login_required
def buscar_obra():
    termo = request.args.get('q', '')  # captura o parâmetro de busca 'q' da URL

    if termo:
        # Exemplo simples: busca obras cujo título contenha o termo (case-insensitive)
        resultados = Content.query.filter(Content.title.ilike(f'%{termo}%')).all()
    else:
        resultados = []

    return render_template('buscar.html', resultados=resultados, termo=termo)


@content_bp.route('/<int:content_id>')
def view_content(content_id):
    """Visualiza um conteúdo específico"""
    content = Content.query.get_or_404(content_id)
    from ..utils.helpers import (
        extract_youtube_id,
        youtube_thumbnail_url,
        youtube_embed_url,
    )
    return render_template(
        'content/view.html',
        content=content,
        extract_youtube_id=extract_youtube_id,
        youtube_thumbnail_url=youtube_thumbnail_url,
        youtube_embed_url=youtube_embed_url,
    )

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
        
        # Validação de tipos permitidos
        allowed_types = ['serie', 'filme', 'documentario', 'anime', 'novela']
        if content_type not in allowed_types:
            flash('Tipo de conteúdo inválido. Selecione um tipo válido.', 'danger')
            return render_template('content/create.html')

        # Converte a data se fornecida
        from ..utils.helpers import parse_date
        release_date_obj = parse_date(release_date)
        if release_date and not release_date_obj:
            return render_template('content/create.html')
        
        # Auto-gerar thumbnail do YouTube quando aplicável
        final_thumbnail = thumbnail
        if url and not final_thumbnail:
            try:
                from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
                video_id = extract_youtube_id(url)
                if video_id:
                    final_thumbnail = youtube_thumbnail_url(video_id, 'hqdefault')
            except Exception:
                pass

        new_content = Content(
            title=title,
            description=description,
            type=content_type,
            url=url,
            thumbnail=final_thumbnail,
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
        content_type = request.form.get('type')
        allowed_types = ['serie', 'filme', 'documentario', 'anime', 'novela']
        if content_type not in allowed_types:
            flash('Tipo de conteúdo inválido. Selecione um tipo válido.', 'danger')
            return render_template('content/edit.html', content=content)
        content.type = content_type
        new_url = request.form.get('url')
        new_thumbnail = request.form.get('thumbnail')
        content.url = new_url
        # Auto-preencher thumbnail se vazio e URL for do YouTube
        if not new_thumbnail and new_url:
            try:
                from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
                video_id = extract_youtube_id(new_url)
                if video_id:
                    new_thumbnail = youtube_thumbnail_url(video_id, 'hqdefault')
            except Exception:
                pass
        content.thumbnail = new_thumbnail
        
        # Atualizar data de lançamento se fornecida
        release_date = request.form.get('release_date')
        if release_date:
            from ..utils.helpers import parse_date
            content.release_date = parse_date(release_date)
        
        db.session.commit()
        flash('Conteúdo atualizado com sucesso!', 'success')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    return render_template('content/edit.html', content=content)

@content_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Upload rápido de imagem para conteúdo. Retorna URL pública."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Arquivo inválido.'}), 400

    filename = secure_filename(file.filename)
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    file_url = url_for('static', filename=f'uploads/{filename}', _external=False)
    return jsonify({'success': True, 'url': file_url})

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