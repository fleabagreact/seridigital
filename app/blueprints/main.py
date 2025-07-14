# app/blueprints/main.py
from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial do site"""
    return render_template('main/index.html', usuario=current_user)