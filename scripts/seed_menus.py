"""
Script para popular os menus iniciais do sistema
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.menu_item import MenuItem
import uuid


def seed_menus():
    """Popula os menus iniciais do sistema"""
    db: Session = SessionLocal()
    
    try:
        # Verificar se já existem menus
        existing_menus = db.query(MenuItem).first()
        if existing_menus:
            print("⚠️  Menus já existem no banco. Pulando seed...")
            return
        
        print("📋 Criando menus iniciais...")
        
        # Menus principais (sem parent)
        menus = [
            {
                "id": uuid.uuid4(),
                "label": "Dashboard",
                "icon": "LayoutDashboard",
                "to": "/dashboard",
                "order": 1,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": None
            },
            {
                "id": uuid.uuid4(),
                "label": "Médicos",
                "icon": "Stethoscope",
                "to": None,  # Será um menu com submenus
                "order": 2,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": None
            },
            {
                "id": uuid.uuid4(),
                "label": "Pacientes",
                "icon": "Users",
                "to": None,  # Será um menu com submenus
                "order": 3,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": None
            },
            {
                "id": uuid.uuid4(),
                "label": "Procedimentos",
                "icon": "FileText",
                "to": None,  # Será um menu com submenus
                "order": 4,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": None
            },
            {
                "id": uuid.uuid4(),
                "label": "Importar",
                "icon": "Upload",
                "to": "/import",
                "order": 5,
                "roles": ["ADMIN"],  # Apenas admin
                "is_active": True,
                "parent_id": None
            },
            {
                "id": uuid.uuid4(),
                "label": "Configurações",
                "icon": "Settings",
                "to": "/settings",
                "order": 6,
                "roles": ["ADMIN"],  # Apenas admin
                "is_active": True,
                "parent_id": None
            }
        ]
        
        # Criar os menus principais primeiro
        created_menus = {}
        for menu_data in menus:
            menu = MenuItem(**menu_data)
            db.add(menu)
            created_menus[menu_data["label"]] = menu
        
        db.flush()  # Para ter os IDs disponíveis
        
        # Submenus de Médicos
        medicos_submenus = [
            {
                "label": "Listar Médicos",
                "icon": "List",
                "to": "/medicos",
                "order": 1,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Médicos"].id
            },
            {
                "label": "Novo Médico",
                "icon": "UserPlus",
                "to": "/medicos/novo",
                "order": 2,
                "roles": ["ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Médicos"].id
            }
        ]
        
        # Submenus de Pacientes
        pacientes_submenus = [
            {
                "label": "Listar Pacientes",
                "icon": "List",
                "to": "/pacientes",
                "order": 1,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Pacientes"].id
            },
            {
                "label": "Novo Paciente",
                "icon": "UserPlus",
                "to": "/pacientes/novo",
                "order": 2,
                "roles": ["ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Pacientes"].id
            }
        ]
        
        # Submenus de Procedimentos
        procedimentos_submenus = [
            {
                "label": "Listar Procedimentos",
                "icon": "List",
                "to": "/procedimentos",
                "order": 1,
                "roles": ["USER", "ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Procedimentos"].id
            },
            {
                "label": "Novo Procedimento",
                "icon": "PlusCircle",
                "to": "/procedimentos/novo",
                "order": 2,
                "roles": ["ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Procedimentos"].id
            },
            {
                "label": "Tipos de Procedimento",
                "icon": "FolderCog",
                "to": "/procedimentos/tipos",
                "order": 3,
                "roles": ["ADMIN"],
                "is_active": True,
                "parent_id": created_menus["Procedimentos"].id
            }
        ]
        
        # Adicionar todos os submenus
        all_submenus = medicos_submenus + pacientes_submenus + procedimentos_submenus
        
        for submenu_data in all_submenus:
            submenu = MenuItem(**submenu_data)
            db.add(submenu)
        
        # Commit no banco
        db.commit()
        
        print("✅ Menus criados com sucesso!")
        print(f"   - {len(menus)} menus principais")
        print(f"   - {len(all_submenus)} submenus")
        print(f"   Total: {len(menus) + len(all_submenus)} itens")
        
    except Exception as e:
        print(f"❌ Erro ao criar menus: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Iniciando seed de menus...")
    seed_menus()
    print("🎉 Processo finalizado!")
