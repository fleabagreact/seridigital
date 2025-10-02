"""
Módulo para aplicar migrações pendentes na inicialização da aplicação
"""
from sqlalchemy import text

def apply_content_migration(db):
    """
    Aplica a migração para adicionar colunas file_path e file_type à tabela tb_contents
    
    Args:
        db: Instância do SQLAlchemy
    """
    try:
        # Verificar se as colunas já existem
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'tb_contents' not in inspector.get_table_names():
            print("⚠️ Tabela tb_contents não existe ainda. Será criada pelo db.create_all()")
            return
        
        columns = [col['name'] for col in inspector.get_columns('tb_contents')]
        
        needs_migration = False
        
        # Adicionar cnt_file_path se não existir
        if 'cnt_file_path' not in columns:
            print("📝 Adicionando coluna cnt_file_path...")
            db.session.execute(text('ALTER TABLE tb_contents ADD COLUMN cnt_file_path VARCHAR(500)'))
            needs_migration = True
        
        # Adicionar cnt_file_type se não existir
        if 'cnt_file_type' not in columns:
            print("📝 Adicionando coluna cnt_file_type...")
            db.session.execute(text('ALTER TABLE tb_contents ADD COLUMN cnt_file_type VARCHAR(10)'))
            needs_migration = True
        
        if needs_migration:
            db.session.commit()
            print("✅ Migração aplicada com sucesso!")
        else:
            print("✓ Banco de dados já está atualizado")
            
    except Exception as e:
        print(f"❌ Erro ao aplicar migração: {e}")
        db.session.rollback()
        raise

def apply_ratings_migration(db):
    """
    Aplica a migração para adicionar coluna review à tabela tb_ratings
    
    Args:
        db: Instância do SQLAlchemy
    """
    try:
        # Verificar se as colunas já existem
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'tb_ratings' not in inspector.get_table_names():
            print("⚠️ Tabela tb_ratings não existe ainda. Será criada pelo db.create_all()")
            return
        
        columns = [col['name'] for col in inspector.get_columns('tb_ratings')]
        
        # Adicionar rat_review se não existir
        if 'rat_review' not in columns:
            print("📝 Adicionando coluna rat_review...")
            db.session.execute(text('ALTER TABLE tb_ratings ADD COLUMN rat_review TEXT'))
            db.session.commit()
            print("✅ Campo rat_review adicionado com sucesso!")
        else:
            print("✓ Campo rat_review já existe na tabela tb_ratings")
            
    except Exception as e:
        print(f"❌ Erro ao aplicar migração de ratings: {e}")
        db.session.rollback()
        raise

def apply_all_migrations(db):
    """
    Aplica todas as migrações pendentes
    
    Args:
        db: Instância do SQLAlchemy
    """
    print("🔄 Aplicando migrações...")
    apply_content_migration(db)
    apply_ratings_migration(db)
    print("✅ Todas as migrações aplicadas!")