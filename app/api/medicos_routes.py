from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.medico import Medico
from app.models.procedimento import Procedimento
from app.schemas.import_schema import MedicoResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/medicos", tags=["medicos"])


@router.get("", response_model=List[MedicoResponse])
def listar_medicos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os médicos cadastrados
    
    - **skip**: Pular N registros (paginação)
    - **limit**: Limitar quantidade de resultados
    - **search**: Buscar por nome ou CRM
    """
    query = db.query(Medico).filter(Medico.ativo == True)
    
    # Filtro de busca
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Medico.nome.ilike(search_filter)) |
            (Medico.crm.ilike(search_filter))
        )
    
    # Ordenar por nome
    query = query.order_by(Medico.nome)
    
    # Paginação
    medicos = query.offset(skip).limit(limit).all()
    
    return [
        MedicoResponse(
            id=str(m.id),
            nome=m.nome,
            crm=m.crm,
            especialidade=m.especialidade
        )
        for m in medicos
    ]


@router.get("/{medico_id}", response_model=dict)
def detalhe_medico(
    medico_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detalhes de um médico específico com estatísticas
    """
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Contar procedimentos deste médico
    total_procedimentos = db.query(func.count(Procedimento.id)).filter(
        Procedimento.medico_id == medico_id
    ).scalar()
    
    # Procedimento mais recente
    ultimo_procedimento = db.query(Procedimento).filter(
        Procedimento.medico_id == medico_id
    ).order_by(Procedimento.data.desc()).first()
    
    return {
        "id": str(medico.id),
        "nome": medico.nome,
        "crm": medico.crm,
        "especialidade": medico.especialidade,
        "email": medico.email,
        "telefone": medico.telefone,
        "ativo": medico.ativo,
        "created_at": medico.created_at.isoformat() if medico.created_at else None,
        "stats": {
            "total_procedimentos": total_procedimentos,
            "ultima_atividade": ultimo_procedimento.data.isoformat() if ultimo_procedimento else None
        }
    }


@router.get("/{medico_id}/procedimentos", response_model=dict)
def procedimentos_do_medico(
    medico_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista procedimentos de um médico específico
    """
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Buscar procedimentos
    procedimentos = db.query(Procedimento).filter(
        Procedimento.medico_id == medico_id
    ).order_by(Procedimento.data.desc()).offset(skip).limit(limit).all()
    
    return {
        "medico": {
            "id": str(medico.id),
            "nome": medico.nome
        },
        "procedimentos": [
            {
                "id": str(p.id),
                "data": p.data.isoformat(),
                "tipo": p.tipo.nome,
                "paciente": p.paciente.nome,
                "valor": float(p.valor) if p.valor else None
            }
            for p in procedimentos
        ],
        "total": len(procedimentos)
    }
