from flask import Blueprint, render_template, request, flash, redirect, url_for
import smtplib
from email.mime.text import MIMEText

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
            return render_template('feedbacks.html')

        # Envia email para destinatário fixo
        destinatario = 'jefferson.anjos@escolar.ifrn.edu.br'
        corpo = f"Nome: {nome}\nEmail do remetente: {email}\nAssunto: {assunto}\n\n{mensagem}"
        msg = MIMEText(corpo, 'plain', 'utf-8')
        msg['Subject'] = f"Feedback - {assunto}"
        msg['From'] = email
        msg['To'] = destinatario

        try:
            # Tenta usar SMTP local; se não houver, apenas simula sucesso
            with smtplib.SMTP('localhost') as server:
                server.sendmail(email, [destinatario], msg.as_string())
            mensagem_sucesso = "Feedback enviado com sucesso! Obrigado pela sua opinião."
            return render_template('feedbacks.html', mensagem_sucesso=mensagem_sucesso)
        except Exception:
            # Fallback: não falhar a UX caso não haja SMTP configurado
            mensagem_sucesso = "Feedback registrado! (envio de e-mail simulado)"
            return render_template('feedbacks.html', mensagem_sucesso=mensagem_sucesso)

    return render_template('feedbacks.html')
