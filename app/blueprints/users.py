# app/blueprints/users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from ..models import Usuario, db, Rating, CommunityPost, CommunityPostComment, CommunityPostLike

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/list')
def list_users():
    """Lista todos os usuários cadastrados"""
    usuarios = Usuario.query.all()
    return render_template('users/list.html', usuarios=usuarios, usuario=current_user)

@users_bp.route('/profile/<int:user_id>')
def profile(user_id):
    """Exibe o perfil de um usuário específico"""
    from sqlalchemy import desc
    from datetime import datetime, timedelta
    
    usuario = Usuario.query.get_or_404(user_id)
    
    # Buscar atividades recentes (últimos 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Avaliações recentes
    recent_ratings = Rating.query.filter(
        Rating.user_id == user_id,
        Rating.created_at >= thirty_days_ago
    ).order_by(desc(Rating.created_at)).limit(5).all()
    
    # Posts em comunidades recentes
    recent_posts = CommunityPost.query.filter(
        CommunityPost.author_id == user_id,
        CommunityPost.created_at >= thirty_days_ago
    ).order_by(desc(CommunityPost.created_at)).limit(5).all()
    
    # Comentários recentes
    recent_comments = CommunityPostComment.query.filter(
        CommunityPostComment.user_id == user_id,
        CommunityPostComment.created_at >= thirty_days_ago
    ).order_by(desc(CommunityPostComment.created_at)).limit(5).all()
    
    # Likes recentes
    recent_likes = CommunityPostLike.query.filter(
        CommunityPostLike.user_id == user_id,
        CommunityPostLike.created_at >= thirty_days_ago
    ).order_by(desc(CommunityPostLike.created_at)).limit(5).all()
    
    # Criar lista unificada de atividades
    activities = []
    
    # Adicionar avaliações
    for rating in recent_ratings:
        if rating.content:  # Verificar se o conteúdo existe
            activities.append({
                'type': 'rating',
                'icon': 'fas fa-star',
                'color': 'warning',
                'title': f'Avaliou "{rating.content.title}"',
                'description': f'{rating.rating} estrelas' + (f' - "{rating.review}"' if rating.review else ''),
                'date': rating.created_at,
                'url': url_for('content.view_content', content_id=rating.content_id)
            })
    
    # Adicionar posts
    for post in recent_posts:
        if post.comunidade:  # Verificar se a comunidade existe
            activities.append({
                'type': 'post',
                'icon': 'fas fa-comment',
                'color': 'primary',
                'title': f'Postou em "{post.comunidade.name}"',
                'description': post.content[:100] + ('...' if len(post.content) > 100 else ''),
                'date': post.created_at,
                'url': url_for('comunidade.comunidade_users', community_id=post.community_id)
            })
    
    # Adicionar comentários
    for comment in recent_comments:
        if comment.post and comment.post.comunidade:  # Verificar se o post e a comunidade existem
            activities.append({
                'type': 'comment',
                'icon': 'fas fa-reply',
                'color': 'info',
                'title': f'Comentou em "{comment.post.comunidade.name}"',
                'description': comment.text[:100] + ('...' if len(comment.text) > 100 else ''),
                'date': comment.created_at,
                'url': url_for('comunidade.comunidade_users', community_id=comment.post.community_id)
            })
    
    # Adicionar likes
    for like in recent_likes:
        if like.post and like.post.comunidade:  # Verificar se o post e a comunidade existem
            activities.append({
                'type': 'like',
                'icon': 'fas fa-heart',
                'color': 'danger',
                'title': f'Curtiu post em "{like.post.comunidade.name}"',
                'description': like.post.content[:100] + ('...' if len(like.post.content) > 100 else ''),
                'date': like.created_at,
                'url': url_for('comunidade.comunidade_users', community_id=like.post.community_id)
            })
    
    # Ordenar atividades por data (mais recente primeiro)
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Limitar a 10 atividades mais recentes
    activities = activities[:10]
    
    return render_template('users/profile.html', usuario=usuario, activities=activities)

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