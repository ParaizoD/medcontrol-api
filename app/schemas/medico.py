# app/schemas/medico.py
# VERSÃO DEFINITIVA - Compatível com UUID

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class MedicoBase(BaseModel):
    nome: str
    crm: str
    especialidade: str
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class MedicoCreate(MedicoBase):
    """Schema para criação de médico"""
    pass


class MedicoUpdate(BaseModel):
    """Schema para atualização parcial de médico"""
    nome: Optional[str] = None
    crm: Optional[str] = None
    especialidade: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class MedicoResponse(MedicoBase):
    """Schema para resposta da API"""
    id: UUID
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # orm_mode = True (versão antiga)


class MedicoList(BaseModel):
    """Schema para lista de médicos"""
    total: int
    medicos: list[MedicoResponse]
