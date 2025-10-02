# app/blueprints/content.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import Content, Rating, db
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
    termo = request.args.get('q', '').strip()  # captura o parâmetro de busca 'q' da URL

    if termo:
        # Busca mais abrangente: título OU descrição
        resultados = Content.query.filter(
            db.or_(
                Content.title.ilike(f'%{termo}%'),
                Content.description.ilike(f'%{termo}%')
            )
        ).order_by(Content.created_at.desc()).all()
    else:
        resultados = []

    return render_template('buscar.html', resultados=resultados, termo=termo)


@content_bp.route('/<int:content_id>')
def view_content(content_id):
    """Visualiza um conteúdo específico"""
    from sqlalchemy import func
    content = Content.query.get_or_404(content_id)
    
    # Buscar todas as avaliações
    ratings = Rating.query.filter_by(content_id=content_id).order_by(Rating.created_at.desc()).all()
    
    # Calcular média das avaliações
    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(content_id=content_id).scalar()
    total_ratings = len(ratings)
    
    # Buscar avaliação do usuário atual se estiver logado
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()
    
    from ..utils.helpers import (
        extract_youtube_id,
        youtube_thumbnail_url,
        youtube_embed_url,
    )
    return render_template(
        'content/view.html',
        content=content,
        ratings=ratings,
        avg_rating=avg_rating,
        total_ratings=total_ratings,
        user_rating=user_rating,
        extract_youtube_id=extract_youtube_id,
        youtube_thumbnail_url=youtube_thumbnail_url,
        youtube_embed_url=youtube_embed_url,
    )

@content_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_content():
    """Cria nova obra (livro ou manifesto)"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content_type = request.form.get('type')
        url = request.form.get('url')  # Link de vídeo relacionado
        thumbnail = request.form.get('thumbnail')
        release_date = request.form.get('release_date')
        
        # Validação de tipos permitidos
        allowed_types = ['livro', 'manifesto']
        if content_type not in allowed_types:
            flash('Tipo de obra inválido. Selecione um tipo válido.', 'danger')
            return render_template('content/create.html')

        # Validar: arquivo OU URL do YouTube é obrigatório
        has_file = request.files.get('file') and request.files.get('file').filename != ''
        has_youtube_url = url and url.strip() != ''
        
        if not has_file and not has_youtube_url:
            flash('É obrigatório fornecer um arquivo (PDF/EPUB) ou um link do YouTube.', 'danger')
            return render_template('content/create.html')
        
        # Processar upload do arquivo (se fornecido)
        relative_path = None
        file_ext = None
        
        file = request.files.get('file')
        if file and file.filename != '':
            # Validar extensão do arquivo
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            if file_ext not in ['pdf', 'epub']:
                flash('Apenas arquivos PDF e EPUB são permitidos.', 'danger')
                return render_template('content/create.html')
            
            # Criar diretório de uploads se não existir
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'obras')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único para o arquivo
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Salvar caminho relativo no banco
            relative_path = f"uploads/obras/{unique_filename}"
        
        # Gerar thumbnail do YouTube automaticamente se não houver thumbnail manual
        if not thumbnail and url:
            from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
            video_id = extract_youtube_id(url)
            if video_id:
                thumbnail = youtube_thumbnail_url(video_id, quality='maxresdefault')

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
            release_date=release_date_obj,
            file_path=relative_path,
            file_type=file_ext
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        flash('Obra criada com sucesso!', 'success')
        return redirect(url_for('content.list_content'))
    
    return render_template('content/create.html')

@content_bp.route('/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_content(content_id):
    """Edita uma obra"""
    content = Content.query.get_or_404(content_id)
    
    if request.method == 'POST':
        content.title = request.form.get('title')
        content.description = request.form.get('description')
        content_type = request.form.get('type')
        allowed_types = ['livro', 'manifesto']
        if content_type not in allowed_types:
            flash('Tipo de obra inválido. Selecione um tipo válido.', 'danger')
            return render_template('content/edit.html', content=content)
        content.type = content_type
        
        # Processar novo arquivo se enviado
        file = request.files.get('file')
        if file and file.filename != '':
            # Validar extensão do arquivo
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            if file_ext not in ['pdf', 'epub']:
                flash('Apenas arquivos PDF e EPUB são permitidos.', 'danger')
                return render_template('content/edit.html', content=content)
            
            # Deletar arquivo antigo se existir
            if content.file_path:
                old_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Salvar novo arquivo
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'obras')
            os.makedirs(upload_dir, exist_ok=True)
            
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            content.file_path = f"uploads/obras/{unique_filename}"
            content.file_type = file_ext
        
        # Atualizar URL de vídeo relacionado
        new_url = request.form.get('url')
        content.url = new_url
        
        # Atualizar thumbnail
        new_thumbnail = request.form.get('thumbnail')
        content.thumbnail = new_thumbnail
        
        # Gerar thumbnail do YouTube automaticamente se não houver thumbnail manual
        if not new_thumbnail and new_url:
            from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
            video_id = extract_youtube_id(new_url)
            if video_id:
                content.thumbnail = youtube_thumbnail_url(video_id, quality='maxresdefault')
        
        # Atualizar data de publicação
        release_date = request.form.get('release_date')
        if release_date:
            from ..utils.helpers import parse_date
            content.release_date = parse_date(release_date)
        
        db.session.commit()
        flash('Obra atualizada com sucesso!', 'success')
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
        # Deletar arquivo físico se existir
        if content.file_path:
            file_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
        
        db.session.delete(content)
        db.session.commit()
        flash('Obra deletada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar obra: {str(e)}', 'danger')
    
    return redirect(url_for('content.list_content'))

@content_bp.route('/<int:content_id>/download')
@login_required
def download_content(content_id):
    """Faz download do arquivo da obra"""
    from flask import send_file
    content = Content.query.get_or_404(content_id)
    
    if not content.file_path:
        flash('Esta obra não possui arquivo disponível para download.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    file_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)
    
    if not os.path.exists(file_full_path):
        flash('Arquivo não encontrado.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    return send_file(file_full_path, as_attachment=True, download_name=f"{content.title}.{content.file_type}")
@content_bp.route('/<int:content_id>/rating', methods=['POST'])
@login_required
def add_rating(content_id):
    """Adiciona ou atualiza avaliação de uma obra"""
    content = Content.query.get_or_404(content_id)
    
    rating_value = request.form.get('rating', type=int)
    review_text = request.form.get('review', '').strip()
    
    if not rating_value or rating_value < 1 or rating_value > 5:
        flash('Avaliação inválida. Selecione de 1 a 5 estrelas.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    # Verificar se usuário já avaliou
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id,
        content_id=content_id
    ).first()
    
    try:
        if existing_rating:
            # Atualizar avaliação existente
            existing_rating.rating = rating_value
            existing_rating.review = review_text if review_text else None
            flash('Sua avaliação foi atualizada!', 'success')
        else:
            # Criar nova avaliação
            new_rating = Rating(
                user_id=current_user.id,
                content_id=content_id,
                rating=rating_value,
                review=review_text if review_text else None
            )
            db.session.add(new_rating)
            flash('Avaliação enviada com sucesso!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar avaliação: {str(e)}', 'danger')
    
    return redirect(url_for('content.view_content', content_id=content_id))

@content_bp.route('/rating/<int:rating_id>/delete', methods=['POST'])
@login_required
def delete_rating(rating_id):
    """Deleta uma avaliação"""
    rating = Rating.query.get_or_404(rating_id)
    content_id = rating.content_id
    
    # Verificar permissão (apenas o autor ou admin pode deletar)
    if current_user.id != rating.user_id and not current_user.is_admin:
        flash('Você não tem permissão para excluir esta avaliação.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    try:
        db.session.delete(rating)
        db.session.commit()
        flash('Avaliação excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir avaliação: {str(e)}', 'danger')
    
    return redirect(url_for('content.view_content', content_id=content_id))