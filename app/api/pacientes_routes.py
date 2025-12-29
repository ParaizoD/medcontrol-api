# app/api/pacientes.py
# VERSÃO DEFINITIVA - Mescla funcionalidades existentes + CRUD completo

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.paciente import Paciente
from app.models.procedimento import Procedimento
from app.schemas.paciente import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteList
)
from app.schemas.import_schema import PacienteResponse as ImportPacienteResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


# ==================== CREATE ====================
@router.post("", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def create_paciente(
    paciente: PacienteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo paciente"""
    
    # Verifica se CPF já existe
    existing = db.query(Paciente).filter(Paciente.cpf == paciente.cpf).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    db_paciente = Paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    
    return db_paciente


# ==================== READ - LIST (MANTÉM SUA VERSÃO COM SEARCH) ====================
@router.get("", response_model=List[ImportPacienteResponse])
def listar_pacientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os pacientes cadastrados
    
    - **skip**: Pular N registros (paginação)
    - **limit**: Limitar quantidade de resultados
    - **search**: Buscar por nome ou CPF
    - **apenas_ativos**: Filtrar apenas pacientes ativos
    """
    query = db.query(Paciente)
    
    # Filtro ativo
    if apenas_ativos:
        query = query.filter(Paciente.ativo == True)
    
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
        ImportPacienteResponse(
            id=str(p.id),
            nome=p.nome,
            cpf=p.cpf
        )
        for p in pacientes
    ]


# ==================== READ - DETAIL (MANTÉM SUA VERSÃO COM STATS) ====================
@router.get("/{paciente_id}", response_model=dict)
def detalhe_paciente(
    paciente_id: UUID,
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
        "observacoes": getattr(paciente, 'observacoes', None),  # Campo opcional
        "ativo": paciente.ativo,
        "created_at": paciente.created_at.isoformat() if paciente.created_at else None,
        "updated_at": paciente.updated_at.isoformat() if paciente.updated_at else None,
        "stats": {
            "total_procedimentos": total_procedimentos,
            "ultima_visita": ultimo_procedimento.data.isoformat() if ultimo_procedimento else None
        }
    }


# ==================== READ - PROCEDIMENTOS DO PACIENTE ====================
@router.get("/{paciente_id}/procedimentos", response_model=dict)
def procedimentos_do_paciente(
    paciente_id: UUID,
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


# ==================== UPDATE - PUT ====================
@router.put("/{paciente_id}", response_model=PacienteResponse)
def update_paciente(
    paciente_id: UUID,
    paciente_data: PacienteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualização completa do paciente (PUT)"""
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {paciente_id} não encontrado"
        )
    
    # Verifica CPF único (se mudou)
    if paciente_data.cpf != paciente.cpf:
        existing = db.query(Paciente).filter(
            Paciente.cpf == paciente_data.cpf,
            Paciente.id != paciente_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado para outro paciente"
            )
    
    # Atualiza todos os campos
    for field, value in paciente_data.dict().items():
        setattr(paciente, field, value)
    
    db.commit()
    db.refresh(paciente)
    
    return paciente


# ==================== UPDATE - PATCH ====================
@router.patch("/{paciente_id}", response_model=PacienteResponse)
def patch_paciente(
    paciente_id: UUID,
    paciente_data: PacienteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualização parcial do paciente (PATCH)"""
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {paciente_id} não encontrado"
        )
    
    # Verifica CPF se estiver sendo atualizado
    if paciente_data.cpf and paciente_data.cpf != paciente.cpf:
        existing = db.query(Paciente).filter(
            Paciente.cpf == paciente_data.cpf,
            Paciente.id != paciente_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado para outro paciente"
            )
    
    # Atualiza apenas campos fornecidos
    update_data = paciente_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(paciente, field, value)
    
    db.commit()
    db.refresh(paciente)
    
    return paciente


# ==================== DELETE ====================
@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paciente(
    paciente_id: UUID,
    force: bool = Query(False, description="Forçar deleção permanente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar paciente
    
    - Se force=False: Faz soft delete (marca como inativo)
    - Se force=True: Deleta permanentemente (só se não houver procedimentos)
    """
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {paciente_id} não encontrado"
        )
    
    if force:
        # Deleção permanente
        procedimentos_count = db.query(Procedimento).filter(
            Procedimento.paciente_id == paciente_id
        ).count()
        
        if procedimentos_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível deletar. Paciente possui {procedimentos_count} procedimento(s) vinculado(s)"
            )
        
        db.delete(paciente)
    else:
        # Soft delete
        paciente.ativo = False
    
    db.commit()
    return None