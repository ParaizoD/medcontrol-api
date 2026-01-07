from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================
# MENU ITEM SCHEMAS
# ============================================

class MenuItemBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=100, description="Label do item do menu")
    icon: Optional[str] = Field(None, max_length=50, description="Nome do ícone (lucide-react)")
    to: Optional[str] = Field(None, max_length=255, description="Path da rota")
    order: int = Field(0, ge=0, description="Ordem de exibição")
    roles: List[str] = Field(default_factory=list, description="Roles que podem ver este menu")
    is_active: bool = Field(True, description="Menu ativo ou inativo")
    parent_id: Optional[str] = Field(None, description="ID do item pai (para submenus)")


class MenuItemCreate(MenuItemBase):
    """Schema para criar um novo item de menu"""
    pass


class MenuItemUpdate(BaseModel):
    """Schema para atualizar um item de menu (todos os campos opcionais)"""
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    to: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None
    parent_id: Optional[str] = None


class MenuItemResponse(BaseModel):
    """Schema de resposta para um item de menu (sem filhos)"""
    id: str
    label: str
    icon: Optional[str]
    to: Optional[str]
    order: int
    roles: List[str]
    is_active: bool
    parent_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MenuItemWithChildren(BaseModel):
    """Schema de resposta com hierarquia (incluindo filhos)"""
    id: str
    label: str
    icon: Optional[str]
    to: Optional[str]
    order: int
    roles: List[str]
    is_active: bool
    parent_id: Optional[str]
    children: List['MenuItemWithChildren'] = []
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Necessário para resolver referência circular
MenuItemWithChildren.model_rebuild()


class MenuItemListResponse(BaseModel):
    """Schema para lista de menus"""
    items: List[MenuItemResponse]
    total: int


class MenuTreeResponse(BaseModel):
    """Schema para árvore de menus"""
    items: List[MenuItemWithChildren]
    total: int
