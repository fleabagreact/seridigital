#Rota responsável por renderizar a página da comunidade e lidar com postagens
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from ..models import db, CommunityPost, Community, CommunityBlock, CommunityPostLike, CommunityPostComment

comunidade_bp = Blueprint('comunidade', __name__, url_prefix='/comunidade')

@comunidade_bp.route('/', methods=['GET'])
@login_required
def comunidade():
    # Usa o novo método para obter comunidades acessíveis
    include_filtered = request.args.get('include_filtered', 'false').lower() == 'true'
    comunidades = current_user.get_accessible_communities(include_filtered=include_filtered)
    return render_template('lista_comunidades.html', comunidades=comunidades)

@comunidade_bp.route('/minhascomunidades/', methods=['GET'])
@login_required
def minhas_comunidades():
    """Lista apenas comunidades em que o usuário é membro (dono ou interagiu)."""
    include_filtered = request.args.get('include_filtered', 'false').lower() == 'true'

    # Subconsultas de participação por posts, comentários e likes
    user_post_communities = db.session.query(CommunityPost.community_id).filter(
        CommunityPost.author_id == current_user.id
    )

    user_comment_communities = (db.session.query(CommunityPost.community_id)
        .join(CommunityPostComment, CommunityPostComment.post_id == CommunityPost.id)
        .filter(CommunityPostComment.user_id == current_user.id)
    )

    user_like_communities = (db.session.query(CommunityPost.community_id)
        .join(CommunityPostLike, CommunityPostLike.post_id == CommunityPost.id)
        .filter(CommunityPostLike.user_id == current_user.id)
    )

    # Comunidades bloqueadas pelo usuário (para exclusão)
    blocked_ids = db.session.query(CommunityBlock.community_id).filter(
        CommunityBlock.user_id == current_user.id
    )

    query = Community.query.filter(Community.status == 'active')

    # Participação: dono ou interagiu (post, comentário, like)
    query = query.filter(
        (
            (Community.owner_id == current_user.id) |
            (Community.id.in_(user_post_communities)) |
            (Community.id.in_(user_comment_communities)) |
            (Community.id.in_(user_like_communities))
        )
    )

    # Excluir bloqueadas
    query = query.filter(~Community.id.in_(blocked_ids))

    # Filtragem de conteúdo sensível
    if not include_filtered:
        query = query.filter(Community.is_filtered.is_(False))

    comunidades = query.order_by(Community.created_at.asc()).all()

    return render_template('lista_comunidades.html', comunidades=comunidades)

@comunidade_bp.route('/minhascomuidades/', methods=['GET'])
@login_required
def minhas_comuidades_alias():
    """Alias com a grafia solicitada, redireciona para a rota correta."""
    return redirect(url_for('comunidade.minhas_comunidades', **request.args))

@comunidade_bp.route('/oficial', methods=['GET'])
@login_required
def comunidade_oficial():
    """Redireciona diretamente para a comunidade oficial SeriDigital"""
    # Buscar comunidade oficial
    comunidade_oficial = Community.query.filter_by(name='SeriDigital').first()
    
    if not comunidade_oficial:
        flash('Comunidade oficial não encontrada.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    # Redirecionar para a comunidade
    return redirect(url_for('comunidade.comunidade_users', community_id=comunidade_oficial.id))

@comunidade_bp.route('/<int:community_id>', methods=['GET', 'POST'])
@login_required
def comunidade_users(community_id):
    comunidade = Community.query.get_or_404(community_id)
    
    # Verifica se o usuário pode acessar a comunidade
    if not comunidade.can_user_access(current_user.id):
        flash('Você não tem permissão para acessar esta comunidade.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    # Verifica se a comunidade está bloqueada pelo usuário
    if current_user.is_community_blocked(community_id):
        flash('Esta comunidade está bloqueada para você.', 'error')
        return redirect(url_for('comunidade.comunidade'))

    if request.method == 'POST':
        texto = request.form.get('mensagem')
        if texto:
            nova_mensagem = CommunityPost(content=texto, author_id=current_user.id, community_id=comunidade.id)
            db.session.add(nova_mensagem)
            db.session.commit()
            return redirect(url_for('comunidade.comunidade_users', community_id=comunidade.id))

    mensagens = CommunityPost.query.filter_by(community_id=comunidade.id).order_by(CommunityPost.created_at.desc()).all()
    return render_template('comunidade.html', comunidade=comunidade, mensagens=mensagens)

@comunidade_bp.route('/<int:community_id>/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(community_id, post_id):
    post = CommunityPost.query.filter_by(id=post_id, community_id=community_id).first_or_404()
    existing = CommunityPostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'liked': False, 'likes_count': CommunityPostLike.query.filter_by(post_id=post.id).count()})
    novo = CommunityPostLike(user_id=current_user.id, post_id=post.id)
    db.session.add(novo)
    db.session.commit()
    return jsonify({'liked': True, 'likes_count': CommunityPostLike.query.filter_by(post_id=post.id).count()})

@comunidade_bp.route('/<int:community_id>/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(community_id, post_id):
    post = CommunityPost.query.filter_by(id=post_id, community_id=community_id).first_or_404()
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'Comentário vazio'}), 400
    comment = CommunityPostComment(user_id=current_user.id, post_id=post.id, text=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'success': True,
        'comments_count': CommunityPostComment.query.filter_by(post_id=post.id).count(),
        'comment': {
            'id': comment.id,
            'author': current_user.nome,
            'text': comment.text,
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
        }
    })

@comunidade_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar_comunidade():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')

        if nome:
            nova_comunidade = Community(owner_id=current_user.id, name=nome, description=descricao)
            db.session.add(nova_comunidade)
            db.session.commit()
            return redirect(url_for('comunidade.comunidade_users', community_id=nova_comunidade.id))

    return render_template('criar_comunidade.html')

@comunidade_bp.route('/delete/<int:community_id>', methods=['POST'])
@login_required
def delete_community(community_id):
    """Deleta uma comunidade (apenas o criador)"""
    comunidade = Community.query.get_or_404(community_id)
    
    # Verificar se o usuário atual é o dono da comunidade
    if comunidade.owner_id != current_user.id:
        flash('Acesso negado. Apenas o criador da comunidade pode apagá-la.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    community_name = comunidade.name
    
    try:
        # Deletar todos os posts relacionados (e seus likes/comentários serão deletados em cascata)
        CommunityPost.query.filter_by(community_id=community_id).delete()
        
        # Deletar todos os bloqueios relacionados à comunidade
        CommunityBlock.query.filter_by(community_id=community_id).delete()
        
        # Deletar a comunidade
        db.session.delete(comunidade)
        db.session.commit()
        
        flash(f'Comunidade "{community_name}" foi apagada com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao apagar comunidade: {str(e)}', 'error')
    
    return redirect(url_for('comunidade.comunidade'))

# Novas rotas para bloqueio e filtragem
@comunidade_bp.route('/block/<int:community_id>', methods=['POST'])
@login_required
def block_community(community_id):
    """Bloqueia uma comunidade para o usuário atual"""
    reason = request.form.get('reason', None)
    
    success, message = current_user.block_community(community_id, reason)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message})
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('comunidade.comunidade'))

@comunidade_bp.route('/unblock/<int:community_id>', methods=['POST'])
@login_required
def unblock_community(community_id):
    """Remove o bloqueio de uma comunidade"""
    success, message = current_user.unblock_community(community_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message})
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('comunidade.comunidade'))

@comunidade_bp.route('/blocked', methods=['GET'])
@login_required
def blocked_communities():
    """Lista todas as comunidades bloqueadas pelo usuário"""
    blocked_communities = current_user.get_blocked_communities()
    return render_template('comunidades_bloqueadas.html', comunidades=blocked_communities)

# Rotas administrativas para gerenciar status das comunidades
@comunidade_bp.route('/admin/block/<int:community_id>', methods=['POST'])
@login_required
def admin_block_community(community_id):
    """Bloqueia uma comunidade (apenas administradores)"""
    if not current_user.is_administrador():
        flash('Acesso negado. Apenas administradores podem realizar esta ação.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    comunidade = Community.query.get_or_404(community_id)
    comunidade.status = 'blocked'
    db.session.commit()
    
    flash(f'Comunidade "{comunidade.name}" foi bloqueada.', 'success')
    return redirect(url_for('comunidade.comunidade'))

@comunidade_bp.route('/admin/unblock/<int:community_id>', methods=['POST'])
@login_required
def admin_unblock_community(community_id):
    """Desbloqueia uma comunidade (apenas administradores)"""
    if not current_user.is_administrador():
        flash('Acesso negado. Apenas administradores podem realizar esta ação.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    comunidade = Community.query.get_or_404(community_id)
    comunidade.status = 'active'
    db.session.commit()
    
    flash(f'Comunidade "{comunidade.name}" foi desbloqueada.', 'success')
    return redirect(url_for('comunidade.comunidade'))

@comunidade_bp.route('/admin/filter/<int:community_id>', methods=['POST'])
@login_required
def admin_filter_community(community_id):
    """Aplica filtro de conteúdo sensível (apenas administradores)"""
    if not current_user.is_administrador():
        flash('Acesso negado. Apenas administradores podem realizar esta ação.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    comunidade = Community.query.get_or_404(community_id)
    reason = request.form.get('reason', 'Conteúdo sensível')
    
    comunidade.is_filtered = True
    comunidade.filter_reason = reason
    db.session.commit()
    
    flash(f'Comunidade "{comunidade.name}" foi marcada como filtrada.', 'success')
    return redirect(url_for('comunidade.comunidade'))

@comunidade_bp.route('/admin/unfilter/<int:community_id>', methods=['POST'])
@login_required
def admin_unfilter_community(community_id):
    """Remove filtro de conteúdo sensível (apenas administradores)"""
    if not current_user.is_administrador():
        flash('Acesso negado. Apenas administradores podem realizar esta ação.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    comunidade = Community.query.get_or_404(community_id)
    comunidade.is_filtered = False
    comunidade.filter_reason = None
    db.session.commit()
    
    flash(f'Comunidade "{comunidade.name}" teve o filtro removido.', 'success')
    return redirect(url_for('comunidade.comunidade'))

@comunidade_bp.route('/<int:community_id>/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(community_id, post_id):
    """Excluir post de uma comunidade"""
    from flask import jsonify
    
    post = CommunityPost.query.get_or_404(post_id)
    comunidade = Community.query.get_or_404(community_id)
    
    # Verificar permissão: autor do post, admin ou dono da comunidade
    if current_user.id != post.user_id and not current_user.is_admin and current_user.id != comunidade.owner_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Sem permissão'}), 403
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('comunidade.comunidade_users', community_id=community_id))
    
    try:
        # Deletar comentários associados
        CommunityPostComment.query.filter_by(post_id=post_id).delete()
        
        # Deletar likes associados
        CommunityPostLike.query.filter_by(post_id=post_id).delete()
        
        # Deletar o post
        db.session.delete(post)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Post excluído'})
        
        flash('Post excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Erro ao excluir post: {str(e)}', 'danger')
    
    return redirect(url_for('comunidade.ver_comunidade', community_id=community_id))

@comunidade_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Excluir comentário de um post"""
    from flask import jsonify
    
    comentario = CommunityPostComment.query.get_or_404(comment_id)
    post_id = comentario.post_id
    post = CommunityPost.query.get(post_id)
    comunidade = Community.query.get(post.community_id) if post else None
    
    # Verificar permissão: autor do comentário, admin ou dono da comunidade
    if current_user.id != comentario.user_id and not current_user.is_admin and (not comunidade or current_user.id != comunidade.owner_id):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Sem permissão'}), 403
        flash('Você não tem permissão para excluir este comentário.', 'danger')
        return redirect(url_for('comunidade.comunidade_users', community_id=post.community_id))
    
    try:
        db.session.delete(comentario)
        db.session.commit()
        
        # Contar comentários restantes
        comments_count = CommunityPostComment.query.filter_by(post_id=post_id).count()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Comentário excluído', 'comments_count': comments_count})
        
        flash('Comentário excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Erro ao excluir comentário: {str(e)}', 'danger')
    
    return redirect(url_for('comunidade.ver_comunidade', community_id=post.community_id))