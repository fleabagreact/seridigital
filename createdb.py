from app import create_app, db
from app.models import (
    Usuario, Follower, PrivateMessage, Community, CommunityPost, CommunityBlock,
    Comment, Like, WatchHistory, Rating, Content, Category, ContentCategory
)

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")
