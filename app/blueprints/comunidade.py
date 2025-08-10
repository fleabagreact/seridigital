#Rota responsável por renderizar a página da comunidade e lidar com postagens
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, CommunityPost, Community

comunidade_bp = Blueprint('comunidade', __name__, url_prefix='/comunidade')

@comunidade_bp.route('/', methods=['GET'])
@login_required
def comunidade():
    comunidades = Community.query.order_by(Community.created_at.asc()).all()
    return render_template('lista_comunidades.html', comunidades=comunidades)

@comunidade_bp.route('/<int:community_id>', methods=['GET', 'POST'])
@login_required
def comunidade_users(community_id):
    comunidade = Community.query.get_or_404(community_id)

    if request.method == 'POST':
        texto = request.form.get('mensagem')
        if texto:
            nova_mensagem = CommunityPost(content=texto, author_id=current_user.id, community_id=comunidade.id)
            db.session.add(nova_mensagem)
            db.session.commit()
            return redirect(url_for('comunidade.comunidade_users', community_id=comunidade.id))

    mensagens = CommunityPost.query.filter_by(community_id=comunidade.id).order_by(CommunityPost.created_at.asc()).all()
    return render_template('comunidade.html', comunidade=comunidade, mensagens=mensagens)

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
