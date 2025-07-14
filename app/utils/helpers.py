# app/utils/helpers.py
from datetime import datetime
from flask import flash

def parse_date(date_string):
    """Converte string de data para objeto date"""
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        flash('Data inválida fornecida.', 'warning')
        return None

def format_date(date_obj, format_str='%d/%m/%Y'):
    """Formata objeto date para string"""
    if not date_obj:
        return ''
    return date_obj.strftime(format_str)

def truncate_text(text, max_length=150):
    """Trunca texto para um tamanho máximo"""
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + '...'