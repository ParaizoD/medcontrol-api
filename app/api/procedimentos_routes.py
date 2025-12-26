from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.procedimento import Procedimento
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.tipo_procedimento import TipoProcedimento
from app.schemas.import_schema import ProcedimentoResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/procedimentos", tags=["procedimentos"])


@router.get("", response_model=dict)
def listar_procedimentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    medico_id: Optional[str] = None,
    paciente_id: Optional[str] = None,
    tipo_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista procedimentos com filtros opcionais
    
    - **data_inicio**: Data inicial (YYYY-MM-DD)
    - **data_fim**: Data final (YYYY-MM-DD)
    - **medico_id**: Filtrar por médico
    - **paciente_id**: Filtrar por paciente
    - **tipo_id**: Filtrar por tipo de procedimento
    """
    query = db.query(Procedimento)
    
    # Aplicar filtros
    if data_inicio:
        query = query.filter(Procedimento.data >= data_inicio)
    
    if data_fim:
        query = query.filter(Procedimento.data <= data_fim)
    
    if medico_id:
        query = query.filter(Procedimento.medico_id == medico_id)
    
    if paciente_id:
        query = query.filter(Procedimento.paciente_id == paciente_id)
    
    if tipo_id:
        query = query.filter(Procedimento.tipo_id == tipo_id)
    
    # Contar total
    total = query.count()
    
    # Ordenar por data (mais recentes primeiro)
    procedimentos = query.order_by(Procedimento.data.desc()).offset(skip).limit(limit).all()
    
    return {
        "procedimentos": [
            {
                "id": str(p.id),
                "data": p.data.isoformat(),
                "tipo": {
                    "id": str(p.tipo.id),
                    "nome": p.tipo.nome,
                    "valor_referencia": float(p.tipo.valor_referencia) if p.tipo.valor_referencia else None
                },
                "medico": {
                    "id": str(p.medico.id),
                    "nome": p.medico.nome,
                    "crm": p.medico.crm
                },
                "paciente": {
                    "id": str(p.paciente.id),
                    "nome": p.paciente.nome
                },
                "valor": float(p.valor) if p.valor else None,
                "observacoes": p.observacoes
            }
            for p in procedimentos
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{procedimento_id}", response_model=dict)
def detalhe_procedimento(
    procedimento_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detalhes completos de um procedimento
    """
    procedimento = db.query(Procedimento).filter(Procedimento.id == procedimento_id).first()
    
    if not procedimento:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    
    return {
        "id": str(procedimento.id),
        "data": procedimento.data.isoformat(),
        "tipo": {
            "id": str(procedimento.tipo.id),
            "nome": procedimento.tipo.nome,
            "descricao": procedimento.tipo.descricao,
            "valor_referencia": float(procedimento.tipo.valor_referencia) if procedimento.tipo.valor_referencia else None
        },
        "medico": {
            "id": str(procedimento.medico.id),
            "nome": procedimento.medico.nome,
            "crm": procedimento.medico.crm,
            "especialidade": procedimento.medico.especialidade,
            "email": procedimento.medico.email,
            "telefone": procedimento.medico.telefone
        },
        "paciente": {
            "id": str(procedimento.paciente.id),
            "nome": procedimento.paciente.nome,
            "cpf": procedimento.paciente.cpf,
            "telefone": procedimento.paciente.telefone,
            "email": procedimento.paciente.email
        },
        "valor": float(procedimento.valor) if procedimento.valor else None,
        "observacoes": procedimento.observacoes,
        "created_at": procedimento.created_at.isoformat() if procedimento.created_at else None
    }
