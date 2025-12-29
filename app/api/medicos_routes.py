# app/api/medicos.py
# VERSÃO DEFINITIVA - Mescla funcionalidades existentes + CRUD completo

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.medico import Medico
from app.models.procedimento import Procedimento
from app.schemas.medico import (
    MedicoCreate,
    MedicoUpdate,
    MedicoResponse,
    MedicoList
)
from app.schemas.import_schema import MedicoResponse as ImportMedicoResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/medicos", tags=["medicos"])


# ==================== CREATE ====================
@router.post("", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def create_medico(
    medico: MedicoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo médico"""
    
    # Verifica se CRM já existe
    existing = db.query(Medico).filter(Medico.crm == medico.crm).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CRM já cadastrado"
        )
    
    db_medico = Medico(**medico.dict())
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    
    return db_medico


# ==================== READ - LIST (MANTÉM SUA VERSÃO COM SEARCH) ====================
@router.get("", response_model=List[ImportMedicoResponse])
def listar_medicos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os médicos cadastrados
    
    - **skip**: Pular N registros (paginação)
    - **limit**: Limitar quantidade de resultados
    - **search**: Buscar por nome ou CRM
    - **apenas_ativos**: Filtrar apenas médicos ativos
    """
    query = db.query(Medico)
    
    # Filtro ativo
    if apenas_ativos:
        query = query.filter(Medico.ativo == True)
    
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
        ImportMedicoResponse(
            id=str(m.id),
            nome=m.nome,
            crm=m.crm,
            especialidade=m.especialidade
        )
        for m in medicos
    ]


# ==================== READ - DETAIL (MANTÉM SUA VERSÃO COM STATS) ====================
@router.get("/{medico_id}", response_model=dict)
def detalhe_medico(
    medico_id: UUID,
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
        "updated_at": medico.updated_at.isoformat() if medico.updated_at else None,
        "stats": {
            "total_procedimentos": total_procedimentos,
            "ultima_atividade": ultimo_procedimento.data.isoformat() if ultimo_procedimento else None
        }
    }


# ==================== READ - PROCEDIMENTOS DO MÉDICO ====================
@router.get("/{medico_id}/procedimentos", response_model=dict)
def procedimentos_do_medico(
    medico_id: UUID,
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


# ==================== UPDATE - PUT ====================
@router.put("/{medico_id}", response_model=MedicoResponse)
def update_medico(
    medico_id: UUID,
    medico_data: MedicoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualização completa do médico (PUT)"""
    
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Médico com ID {medico_id} não encontrado"
        )
    
    # Verifica CRM único (se mudou)
    if medico_data.crm != medico.crm:
        existing = db.query(Medico).filter(
            Medico.crm == medico_data.crm,
            Medico.id != medico_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CRM já cadastrado para outro médico"
            )
    
    # Atualiza todos os campos
    for field, value in medico_data.dict().items():
        setattr(medico, field, value)
    
    db.commit()
    db.refresh(medico)
    
    return medico


# ==================== UPDATE - PATCH ====================
@router.patch("/{medico_id}", response_model=MedicoResponse)
def patch_medico(
    medico_id: UUID,
    medico_data: MedicoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualização parcial do médico (PATCH)"""
    
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Médico com ID {medico_id} não encontrado"
        )
    
    # Verifica CRM se estiver sendo atualizado
    if medico_data.crm and medico_data.crm != medico.crm:
        existing = db.query(Medico).filter(
            Medico.crm == medico_data.crm,
            Medico.id != medico_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CRM já cadastrado para outro médico"
            )
    
    # Atualiza apenas campos fornecidos
    update_data = medico_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medico, field, value)
    
    db.commit()
    db.refresh(medico)
    
    return medico


# ==================== DELETE ====================
@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medico(
    medico_id: UUID,
    force: bool = Query(False, description="Forçar deleção permanente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar médico
    
    - Se force=False: Faz soft delete (marca como inativo)
    - Se force=True: Deleta permanentemente (só se não houver procedimentos)
    """
    
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Médico com ID {medico_id} não encontrado"
        )
    
    if force:
        # Deleção permanente
        procedimentos_count = db.query(Procedimento).filter(
            Procedimento.medico_id == medico_id
        ).count()
        
        if procedimentos_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível deletar. Médico possui {procedimentos_count} procedimento(s) vinculado(s)"
            )
        
        db.delete(medico)
    else:
        # Soft delete
        medico.ativo = False
    
    db.commit()
    return None