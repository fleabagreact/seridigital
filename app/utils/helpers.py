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

# --- YouTube helpers ---
def extract_youtube_id(url: str) -> str | None:
    """Extrai o ID de um vídeo do YouTube a partir de várias formas de URL.

    Exemplos aceitos:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID&ab_channel=Foo
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - http(s)://m.youtube.com/watch?v=VIDEO_ID
    """
    if not url:
        return None

    try:
        import re

        # Padrões comuns de ID do YouTube (11 caracteres, letras/números/_ -)
        id_pattern = r"([a-zA-Z0-9_-]{11})"

        # Tentativas por padrões de URL
        patterns = [
            r"(?:v=)" + id_pattern,                 # watch?v=VIDEOID
            r"youtu\.be/" + id_pattern,           # youtu.be/VIDEOID
            r"youtube\.com/embed/" + id_pattern,  # youtube.com/embed/VIDEOID
            r"youtube\.com/shorts/" + id_pattern  # shorts
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
    except Exception:
        return None

    return None


def youtube_thumbnail_url(video_id: str, quality: str = "hqdefault") -> str:
    """Constrói a URL da miniatura do YouTube para um determinado ID.

    Qualidades comuns: default, mqdefault, hqdefault, sddefault, maxresdefault
    """
    if not video_id:
        return ""
    return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


def youtube_embed_url(video_id: str, autoplay: bool = True) -> str:
    """Retorna a URL de incorporação (embed) para o vídeo."""
    if not video_id:
        return ""
    auto = 1 if autoplay else 0
    # modestbranding e rel=0 para reduzir distrações
    return (
        f"https://www.youtube.com/embed/{video_id}?autoplay={auto}&rel=0&modestbranding=1"
    )