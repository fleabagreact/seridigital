from app import create_app
from app.models import db, Usuario, Follower, PrivateMessage, Community, CommunityPost, CommunityBlock, Comment, Like, WatchHistory, Rating, Content, Category, ContentCategory, CommunityPostLike, CommunityPostComment
import sys

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        print("Banco de dados criado/atualizado com sucesso!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['initdb', 'createdb', 'migratedb']:
        init_db()
    else:
        app.run(debug=True)