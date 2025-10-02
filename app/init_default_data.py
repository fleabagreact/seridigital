"""
Módulo para criar dados padrão: conta SeriDigital e comunidade oficial
"""
from .models import db, Usuario, Community

def create_default_account_and_community():
    """
    Cria a conta oficial SeriDigital e a comunidade padrão
    """
    try:
        # Verificar se a conta SeriDigital já existe
        seridigital_user = Usuario.query.filter_by(email='seridigital@oficial').first()
        
        if not seridigital_user:
            print("📝 Criando conta oficial SeriDigital...")
            seridigital_user = Usuario(
                nome='SeriDigital',
                email='seridigital@oficial',
                is_admin=True  # Conta oficial é administradora
            )
            seridigital_user.senha = 'seridigital123'  # Usa o setter que gera hash
            db.session.add(seridigital_user)
            db.session.commit()
            print("✅ Conta SeriDigital criada com sucesso!")
        else:
            print("✓ Conta SeriDigital já existe")
        
        # Verificar se a comunidade SeriDigital já existe
        seridigital_community = Community.query.filter_by(name='SeriDigital').first()
        
        if not seridigital_community:
            print("📝 Criando comunidade oficial SeriDigital...")
            seridigital_community = Community(
                owner_id=seridigital_user.id,
                name='SeriDigital',
                description='Comunidade oficial do SeriDigital. Participe das discussões sobre livros, manifestos e cultura digital!',
                status='active',
                is_filtered=False
            )
            db.session.add(seridigital_community)
            db.session.commit()
            print("✅ Comunidade SeriDigital criada com sucesso!")
        else:
            print("✓ Comunidade SeriDigital já existe")
            
    except Exception as e:
        print(f"❌ Erro ao criar dados padrão: {e}")
        db.session.rollback()
        raise
