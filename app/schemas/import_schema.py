from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# ============================================
# IMPORT SCHEMAS
# ============================================

class ImportRow(BaseModel):
    """Linha individual do CSV"""
    data: str  # Pode vir como DD/MM/YYYY ou YYYY-MM-DD
    nomeProcedimento: str
    nomeMedicos: str
    nomePaciente: str


class ImportRequest(BaseModel):
    """Request de importação"""
    rows: List[ImportRow]


class ImportResult(BaseModel):
    """Resultado da importação"""
    success: int  # Quantidade de procedimentos criados
    errors: List[dict]  # Lista de erros: [{row: int, message: str}]
    created: dict  # Quantidades criadas: {medicos: int, pacientes: int, ...}
    warnings: List[str]  # Avisos gerais


# ============================================
# ENTITY SCHEMAS (para resposta)
# ============================================

class MedicoResponse(BaseModel):
    id: str
    nome: str
    crm: Optional[str] = None
    especialidade: Optional[str] = None
    
    class Config:
        from_attributes = True


class PacienteResponse(BaseModel):
    id: str
    nome: str
    cpf: Optional[str] = None
    
    class Config:
        from_attributes = True


class TipoProcedimentoResponse(BaseModel):
    id: str
    nome: str
    valor_referencia: Optional[float] = None
    
    class Config:
        from_attributes = True


class ProcedimentoResponse(BaseModel):
    id: str
    data: date
    tipo: TipoProcedimentoResponse
    medico: MedicoResponse
    paciente: PacienteResponse
    valor: Optional[float] = None
    observacoes: Optional[str] = None
    
    class Config:
        from_attributes = True
