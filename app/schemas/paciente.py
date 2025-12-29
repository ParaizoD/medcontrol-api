# app/schemas/paciente.py
# VERSÃO DEFINITIVA - Compatível com UUID

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class PacienteBase(BaseModel):
    nome: str
    cpf: str
    data_nascimento: date
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None


class PacienteCreate(PacienteBase):
    """Schema para criação de paciente"""
    pass


class PacienteUpdate(BaseModel):
    """Schema para atualização parcial de paciente"""
    nome: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None


class PacienteResponse(PacienteBase):
    """Schema para resposta da API"""
    id: UUID
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PacienteList(BaseModel):
    """Schema para lista de pacientes"""
    total: int
    pacientes: list[PacienteResponse]
