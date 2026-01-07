from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.menu_item import MenuItem
from app.models.user import User
from app.schemas.menu_schema import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemResponse,
    MenuItemWithChildren,
    MenuTreeResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/menus", tags=["menus"])


def has_role(user: User, required_roles: List[str]) -> bool:
    """Verifica se o usuário tem algum dos roles necessários"""
    if not required_roles:  # Se não tem roles definidos, todos podem ver
        return True
    
    user_roles = []
    if user.is_admin:
        user_roles.append("ADMIN")
    user_roles.append("USER")
    
    return any(role in required_roles for role in user_roles)


def build_menu_tree(items: List[MenuItem], user: User) -> List[MenuItemWithChildren]:
    """Constrói a árvore de menus hierárquica"""
    # Filtrar apenas itens ativos e que o usuário tem acesso
    filtered_items = [
        item for item in items 
        if item.is_active and has_role(user, item.roles)
    ]
    
    # Criar dicionário para acesso rápido
    items_dict = {str(item.id): item for item in filtered_items}
    
    # Separar itens raiz dos filhos
    root_items = []
    for item in filtered_items:
        if item.parent_id is None:
            root_items.append(item)
    
    # Função recursiva para construir árvore
    def build_node(item: MenuItem) -> MenuItemWithChildren:
        children = [
            build_node(child) 
            for child in filtered_items 
            if child.parent_id == item.id
        ]
        
        return MenuItemWithChildren(
            id=str(item.id),
            label=item.label,
            icon=item.icon,
            to=item.to,
            order=item.order,
            roles=item.roles,
            is_active=item.is_active,
            parent_id=str(item.parent_id) if item.parent_id else None,
            children=sorted(children, key=lambda x: x.order),
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    tree = [build_node(item) for item in root_items]
    return sorted(tree, key=lambda x: x.order)


@router.get("/my-menus", response_model=List[MenuItemWithChildren])
def get_my_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os menus que o usuário atual tem permissão de ver
    
    Este endpoint constrói a árvore hierárquica de menus baseado nos roles do usuário.
    """
    # Buscar todos os menus
    all_items = db.query(MenuItem).all()
    
    # Construir árvore considerando permissões
    menu_tree = build_menu_tree(all_items, current_user)
    
    return menu_tree


@router.get("/tree", response_model=MenuTreeResponse)
def get_menu_tree(
    show_inactive: bool = Query(False, description="Incluir menus inativos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna a árvore completa de menus (apenas admins)
    
    - **show_inactive**: Se True, inclui menus inativos
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem acessar")
    
    query = db.query(MenuItem)
    
    if not show_inactive:
        query = query.filter(MenuItem.is_active == True)
    
    all_items = query.all()
    
    # Para admin, mostrar tudo sem filtro de role
    items_dict = {str(item.id): item for item in all_items}
    root_items = [item for item in all_items if item.parent_id is None]
    
    def build_admin_node(item: MenuItem) -> MenuItemWithChildren:
        children = [
            build_admin_node(child) 
            for child in all_items 
            if child.parent_id == item.id
        ]
        
        return MenuItemWithChildren(
            id=str(item.id),
            label=item.label,
            icon=item.icon,
            to=item.to,
            order=item.order,
            roles=item.roles,
            is_active=item.is_active,
            parent_id=str(item.parent_id) if item.parent_id else None,
            children=sorted(children, key=lambda x: x.order),
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    tree = [build_admin_node(item) for item in root_items]
    tree = sorted(tree, key=lambda x: x.order)
    
    return MenuTreeResponse(items=tree, total=len(tree))


@router.get("", response_model=List[MenuItemResponse])
def list_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    show_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os menus (flat list, apenas admins)
    
    - **skip**: Pular N registros
    - **limit**: Limitar quantidade de resultados
    - **search**: Buscar por label
    - **show_inactive**: Incluir menus inativos
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem acessar")
    
    query = db.query(MenuItem)
    
    if not show_inactive:
        query = query.filter(MenuItem.is_active == True)
    
    if search:
        query = query.filter(MenuItem.label.ilike(f"%{search}%"))
    
    query = query.order_by(MenuItem.order)
    items = query.offset(skip).limit(limit).all()
    
    return [
        MenuItemResponse(
            id=str(item.id),
            label=item.label,
            icon=item.icon,
            to=item.to,
            order=item.order,
            roles=item.roles,
            is_active=item.is_active,
            parent_id=str(item.parent_id) if item.parent_id else None,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        for item in items
    ]


@router.get("/{menu_id}", response_model=MenuItemResponse)
def get_menu(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna detalhes de um menu específico (apenas admins)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem acessar")
    
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu não encontrado")
    
    return MenuItemResponse(
        id=str(menu.id),
        label=menu.label,
        icon=menu.icon,
        to=menu.to,
        order=menu.order,
        roles=menu.roles,
        is_active=menu.is_active,
        parent_id=str(menu.parent_id) if menu.parent_id else None,
        created_at=menu.created_at,
        updated_at=menu.updated_at
    )


@router.post("", response_model=MenuItemResponse, status_code=201)
def create_menu(
    menu_data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo item de menu (apenas admins)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar menus")
    
    # Validar parent_id se fornecido
    if menu_data.parent_id:
        parent = db.query(MenuItem).filter(MenuItem.id == menu_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Menu pai não encontrado")
    
    # Criar novo menu
    new_menu = MenuItem(
        label=menu_data.label,
        icon=menu_data.icon,
        to=menu_data.to,
        order=menu_data.order,
        roles=menu_data.roles,
        is_active=menu_data.is_active,
        parent_id=menu_data.parent_id
    )
    
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    
    return MenuItemResponse(
        id=str(new_menu.id),
        label=new_menu.label,
        icon=new_menu.icon,
        to=new_menu.to,
        order=new_menu.order,
        roles=new_menu.roles,
        is_active=new_menu.is_active,
        parent_id=str(new_menu.parent_id) if new_menu.parent_id else None,
        created_at=new_menu.created_at,
        updated_at=new_menu.updated_at
    )


@router.put("/{menu_id}", response_model=MenuItemResponse)
def update_menu(
    menu_id: str,
    menu_data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um item de menu (apenas admins)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar menus")
    
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu não encontrado")
    
    # Validar parent_id se fornecido
    if menu_data.parent_id:
        # Não permitir que um menu seja pai de si mesmo
        if menu_data.parent_id == menu_id:
            raise HTTPException(status_code=400, detail="Um menu não pode ser pai de si mesmo")
        
        parent = db.query(MenuItem).filter(MenuItem.id == menu_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Menu pai não encontrado")
    
    # Atualizar campos
    update_data = menu_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu, field, value)
    
    db.commit()
    db.refresh(menu)
    
    return MenuItemResponse(
        id=str(menu.id),
        label=menu.label,
        icon=menu.icon,
        to=menu.to,
        order=menu.order,
        roles=menu.roles,
        is_active=menu.is_active,
        parent_id=str(menu.parent_id) if menu.parent_id else None,
        created_at=menu.created_at,
        updated_at=menu.updated_at
    )


@router.delete("/{menu_id}", status_code=204)
def delete_menu(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta um item de menu (apenas admins)
    
    Atenção: Isso deletará também todos os submenus (cascade)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar menus")
    
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu não encontrado")
    
    db.delete(menu)
    db.commit()
    
    return None
