from app import create_app
from app import db  
from app import models  

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")
