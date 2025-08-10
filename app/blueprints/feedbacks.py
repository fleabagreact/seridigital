from flask import Blueprint, render_template, request, flash, redirect, url_for

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('/', methods=['GET', 'POST'])
def enviar_feedback():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')

        # Validação simples
        if not nome or not email or not assunto or not mensagem:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('feedback.html')

        # Aqui você pode salvar no banco de dados ou enviar um email
        # Exemplo simples: só mostrar mensagem de sucesso

        mensagem_sucesso = "Obrigado pelo seu feedback! Nós valorizamos sua opinião."
        return render_template('feedbacks.html', mensagem_sucesso=mensagem_sucesso)

    return render_template('feedbacks.html')
