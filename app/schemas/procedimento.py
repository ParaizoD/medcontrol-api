# app/schemas/procedimento.py
# VERSÃO DEFINITIVA - Compatível com UUID

from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class ProcedimentoBase(BaseModel):
    medico_id: UUID
    paciente_id: UUID
    tipo_procedimento: str
    data_procedimento: date
    valor: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    observacoes: Optional[str] = None


class ProcedimentoCreate(ProcedimentoBase):
    """Schema para criação de procedimento"""
    pass


class ProcedimentoUpdate(BaseModel):
    """Schema para atualização parcial de procedimento"""
    medico_id: Optional[UUID] = None
    paciente_id: Optional[UUID] = None
    tipo_procedimento: Optional[str] = None
    data_procedimento: Optional[date] = None
    valor: Optional[Decimal] = None
    observacoes: Optional[str] = None


class ProcedimentoResponse(ProcedimentoBase):
    """Schema para resposta da API"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProcedimentoList(BaseModel):
    """Schema para lista de procedimentos"""
    total: int
    procedimentos: list[ProcedimentoResponse]


class ProcedimentoWithDetails(ProcedimentoResponse):
    """Schema com detalhes de médico e paciente"""
    medico_nome: str
    medico_crm: str
    paciente_nome: str
    paciente_cpf: str
