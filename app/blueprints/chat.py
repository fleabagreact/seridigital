#Rota responsável por gerenciar o chat privado entre usuários, EM DESENVOLVIMENTO
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.extensions import db
from app.models import PrivateMessage, Usuario
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    message = PrivateMessage(
        sender_id=current_user.id,
        receiver_id=data['receiver_id'],
        text=data['text'],
        sent_at=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({'status': 'success', 'message_id': message.id})

@chat_bp.route('/get_messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    messages = PrivateMessage.query.filter(
        ((PrivateMessage.sender_id == current_user.id) & (PrivateMessage.receiver_id == user_id)) |
        ((PrivateMessage.sender_id == user_id) & (PrivateMessage.receiver_id == current_user.id))
    ).order_by(PrivateMessage.sent_at).all()

    return jsonify([
        {
            'id': m.id,
            'text': m.text,
            'timestamp': m.sent_at.strftime('%d/%m/%Y %H:%M'),
            'from': 'me' if m.sender_id == current_user.id else 'them'
        } for m in messages
    ])
