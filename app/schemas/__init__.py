from app.schemas.auth import *
from app.schemas.medico import (
    MedicoBase,
    MedicoCreate,
    MedicoUpdate,
    MedicoResponse,
    MedicoList
)
from app.schemas.paciente import (
    PacienteBase,
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteList
)
from app.schemas.procedimento import (
    ProcedimentoBase,
    ProcedimentoCreate,
    ProcedimentoUpdate,
    ProcedimentoResponse,
    ProcedimentoList,
    ProcedimentoWithDetails
)

__all__ = [
    # Auth schemas (já existentes)
    # MedicoSchemas
    "MedicoBase",
    "MedicoCreate",
    "MedicoUpdate",
    "MedicoResponse",
    "MedicoList",
    # Paciente schemas
    "PacienteBase",
    "PacienteCreate",
    "PacienteUpdate",
    "PacienteResponse",
    "PacienteList",
    # Procedimento schemas
    "ProcedimentoBase",
    "ProcedimentoCreate",
    "ProcedimentoUpdate",
    "ProcedimentoResponse",
    "ProcedimentoList",
    "ProcedimentoWithDetails"
]