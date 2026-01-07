from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.paciente import Paciente
from app.models.procedimento import Procedimento
from app.schemas.import_schema import PacienteResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("", response_model=List[PacienteResponse])
def listar_pacientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os pacientes cadastrados
    
    - **skip**: Pular N registros (paginação)
    - **limit**: Limitar quantidade de resultados
    - **search**: Buscar por nome ou CPF
    """
    query = db.query(Paciente)
    
    # Filtro de busca
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Paciente.nome.ilike(search_filter)) |
            (Paciente.cpf.ilike(search_filter))
        )
    
    # Ordenar por nome
    query = query.order_by(Paciente.nome)
    
    # Paginação
    pacientes = query.offset(skip).limit(limit).all()
    
    return [
        PacienteResponse(
            id=str(p.id),
            nome=p.nome,
            cpf=p.cpf
        )
        for p in pacientes
    ]


@router.get("/{paciente_id}", response_model=dict)
def detalhe_paciente(
    paciente_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detalhes de um paciente específico com estatísticas
    """
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Contar procedimentos deste paciente
    total_procedimentos = db.query(func.count(Procedimento.id)).filter(
        Procedimento.paciente_id == paciente_id
    ).scalar()
    
    # Procedimento mais recente
    ultimo_procedimento = db.query(Procedimento).filter(
        Procedimento.paciente_id == paciente_id
    ).order_by(Procedimento.data.desc()).first()
    
    return {
        "id": str(paciente.id),
        "nome": paciente.nome,
        "cpf": paciente.cpf,
        "data_nascimento": paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
        "telefone": paciente.telefone,
        "email": paciente.email,
        "endereco": paciente.endereco,
        "observacoes": paciente.observacoes,
        "created_at": paciente.created_at.isoformat() if paciente.created_at else None,
        "stats": {
            "total_procedimentos": total_procedimentos,
            "ultima_visita": ultimo_procedimento.data.isoformat() if ultimo_procedimento else None
        }
    }


@router.get("/{paciente_id}/procedimentos", response_model=dict)
def procedimentos_do_paciente(
    paciente_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista procedimentos de um paciente específico
    """
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Buscar procedimentos
    procedimentos = db.query(Procedimento).filter(
        Procedimento.paciente_id == paciente_id
    ).order_by(Procedimento.data.desc()).offset(skip).limit(limit).all()
    
    return {
        "paciente": {
            "id": str(paciente.id),
            "nome": paciente.nome
        },
        "procedimentos": [
            {
                "id": str(p.id),
                "data": p.data.isoformat(),
                "tipo": p.tipo.nome,
                "medico": p.medico.nome,
                "valor": float(p.valor) if p.valor else None
            }
            for p in procedimentos
        ],
        "total": len(procedimentos)
    }
