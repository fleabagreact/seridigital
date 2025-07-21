#Rota responsável por renderizar a página da comunidade e lidar com postagens
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, CommunityPost

comunidade_bp = Blueprint('comunidade', __name__, url_prefix='/comunidade')

@comunidade_bp.route('/', methods=['GET', 'POST'])
@login_required
def comunidade():
    if request.method == 'POST':
        texto = request.form.get('mensagem')  # nome do campo no form
        if texto:
            nova_mensagem = CommunityPost(content=texto, author_id=current_user.id)
            db.session.add(nova_mensagem)
            db.session.commit()
            return redirect(url_for('comunidade.comunidade'))
    mensagens = CommunityPost.query.order_by(CommunityPost.created_at.asc()).all()
    return render_template('comunidade.html', mensagens=mensagens)

    