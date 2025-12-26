"""
Script para criar usuário inicial no banco de dados

Uso:
    python scripts/create_user.py
    
ou com argumentos:
    python scripts/create_user.py --email admin@medcontrol.com --name Admin --password admin123 --admin
"""

import sys
import os
from getpass import getpass

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash


def create_user(
    email: str,
    name: str,
    password: str,
    is_admin: bool = False
) -> User:
    """Cria um novo usuário no banco"""
    
    db: Session = SessionLocal()
    
    try:
        # Verificar se usuário já existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Usuário com email {email} já existe!")
            return None
        
        # Criar usuário
        user = User(
            email=email,
            name=name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_admin=is_admin
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.name}")
        print(f"   Admin: {'Sim' if user.is_admin else 'Não'}")
        print(f"   ID: {user.id}")
        
        return user
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def main():
    """Função principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Criar usuário no MedControl')
    parser.add_argument('--email', help='Email do usuário')
    parser.add_argument('--name', help='Nome do usuário')
    parser.add_argument('--password', help='Senha do usuário')
    parser.add_argument('--admin', action='store_true', help='Criar como admin')
    
    args = parser.parse_args()
    
    # Se argumentos não fornecidos, pedir interativamente
    email = args.email or input('Email: ')
    name = args.name or input('Nome: ')
    password = args.password or getpass('Senha: ')
    is_admin = args.admin
    
    if not is_admin:
        admin_input = input('Tornar admin? (s/n): ').lower()
        is_admin = admin_input == 's'
    
    # Criar tabelas se não existirem
    print("📦 Criando tabelas no banco...")
    Base.metadata.create_all(bind=engine)
    
    # Criar usuário
    print("👤 Criando usuário...")
    create_user(email, name, password, is_admin)


if __name__ == "__main__":
    main()
