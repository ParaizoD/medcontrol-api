# app/api/procedimentos.py
# VERSÃO DEFINITIVA - Mescla funcionalidades existentes + CRUD completo

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

from app.database import get_db
from app.models.procedimento import Procedimento
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.tipo_procedimento import TipoProcedimento
from app.schemas.procedimento import (
    ProcedimentoCreate,
    ProcedimentoUpdate,
    ProcedimentoResponse,
    ProcedimentoList
)
from app.schemas.import_schema import ProcedimentoResponse as ImportProcedimentoResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/procedimentos", tags=["procedimentos"])


# ==================== CREATE ====================
@router.post("", response_model=ProcedimentoResponse, status_code=status.HTTP_201_CREATED)
def create_procedimento(
    procedimento: ProcedimentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo procedimento"""
    
    # Valida médico
    medico = db.query(Medico).filter(Medico.id == procedimento.medico_id).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Médico com ID {procedimento.medico_id} não encontrado"
        )
    
    # Valida paciente
    paciente = db.query(Paciente).filter(Paciente.id == procedimento.paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {procedimento.paciente_id} não encontrado"
        )
    
    # Valida tipo de procedimento (se fornecido)
    if hasattr(procedimento, 'tipo_id') and procedimento.tipo_id:
        tipo = db.query(TipoProcedimento).filter(TipoProcedimento.id == procedimento.tipo_id).first()
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de procedimento com ID {procedimento.tipo_id} não encontrado"
            )
    
    db_procedimento = Procedimento(**procedimento.dict())
    db.add(db_procedimento)
    db.commit()
    db.refresh(db_procedimento)
    
    return db_procedimento


# ==================== READ - LIST (MANTÉM SUA VERSÃO COM FILTROS) ====================
@router.get("", response_model=dict)
def listar_procedimentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    medico_id: Optional[UUID] = None,
    paciente_id: Optional[UUID] = None,
    tipo_id: Optional[UUID] = None,
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


# ==================== READ - DETAIL (MANTÉM SUA VERSÃO COMPLETA) ====================
@router.get("/{procedimento_id}", response_model=dict)
def detalhe_procedimento(
    procedimento_id: UUID,
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
        "created_at": procedimento.created_at.isoformat() if procedimento.created_at else None,
        "updated_at": procedimento.updated_at.isoformat() if procedimento.updated_at else None
    }


# ==================== UPDATE - PUT ====================
@router.put("/{procedimento_id}", response_model=ProcedimentoResponse)
def update_procedimento(
    procedimento_id: UUID,
    procedimento_data: ProcedimentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualização completa do procedimento (PUT)"""
    
    procedimento = db.query(Procedimento).filter(Procedimento.id == procedimento_id).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procedimento com ID {procedimento_id} não encontrado"
        )
    
    # Valida médico
    medico = db.query(Medico).filter(Medico.id == procedimento_data.medico_id).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Médico com ID {procedimento_data.medico_id} não encontrado"
        )
    
    # Valida paciente
    paciente = db.query(Paciente).filter(Paciente.id == procedimento_data.paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {procedimento_data.paciente_id} não encontrado"
        )
    
    # Valida tipo (se fornecido)
    if hasattr(procedimento_data, 'tipo_id') and procedimento_data.tipo_id:
        tipo = db.query(TipoProcedimento).filter(TipoProcedimento.id == procedimento_data.tipo_id).first()
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de procedimento com ID {procedimento_data.tipo_id} não encontrado"
            )
    
    # Atualiza campos
    for field, value in procedimento_data.dict().items():
        setattr(procedimento, field, value)
    
    # Atualiza timestamp
    if hasattr(procedimento, 'updated_at'):
        procedimento.updated_at = datetime.now()
    
    db.commit()
    db.refresh(procedimento)
    
    return procedimento


# ==================== UPDATE - PATCH ====================
@router.patch("/{procedimento_id}", response_model=ProcedimentoResponse)
def patch_procedimento(
    procedimento_id: UUID,
    procedimento_data: ProcedimentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualização parcial do procedimento (PATCH)"""
    
    procedimento = db.query(Procedimento).filter(Procedimento.id == procedimento_id).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procedimento com ID {procedimento_id} não encontrado"
        )
    
    # Valida médico se fornecido
    if procedimento_data.medico_id:
        medico = db.query(Medico).filter(Medico.id == procedimento_data.medico_id).first()
        if not medico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Médico com ID {procedimento_data.medico_id} não encontrado"
            )
    
    # Valida paciente se fornecido
    if procedimento_data.paciente_id:
        paciente = db.query(Paciente).filter(Paciente.id == procedimento_data.paciente_id).first()
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente com ID {procedimento_data.paciente_id} não encontrado"
            )
    
    # Valida tipo se fornecido
    if hasattr(procedimento_data, 'tipo_id') and procedimento_data.tipo_id:
        tipo = db.query(TipoProcedimento).filter(TipoProcedimento.id == procedimento_data.tipo_id).first()
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de procedimento com ID {procedimento_data.tipo_id} não encontrado"
            )
    
    # Atualiza apenas campos fornecidos
    update_data = procedimento_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(procedimento, field, value)
    
    # Atualiza timestamp
    if hasattr(procedimento, 'updated_at'):
        procedimento.updated_at = datetime.now()
    
    db.commit()
    db.refresh(procedimento)
    
    return procedimento


# ==================== DELETE ====================
@router.delete("/{procedimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_procedimento(
    procedimento_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar procedimento
    
    Procedimentos podem ser deletados permanentemente pois são registros
    e não entidades que outros dados dependem.
    """
    
    procedimento = db.query(Procedimento).filter(Procedimento.id == procedimento_id).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procedimento com ID {procedimento_id} não encontrado"
        )
    
    db.delete(procedimento)
    db.commit()
    
    return None


# ==================== EXTRA: ESTATÍSTICAS ====================
@router.get("/stats/resumo", response_model=dict)
def estatisticas_procedimentos(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    medico_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Estatísticas gerais de procedimentos
    """
    query = db.query(Procedimento)
    
    # Aplicar filtros
    if data_inicio:
        query = query.filter(Procedimento.data >= data_inicio)
    if data_fim:
        query = query.filter(Procedimento.data <= data_fim)
    if medico_id:
        query = query.filter(Procedimento.medico_id == medico_id)
    
    total_procedimentos = query.count()
    
    # Valor total
    valor_total = db.query(func.sum(Procedimento.valor)).filter(
        *[f for f in [
            Procedimento.data >= data_inicio if data_inicio else None,
            Procedimento.data <= data_fim if data_fim else None,
            Procedimento.medico_id == medico_id if medico_id else None
        ] if f is not None]
    ).scalar() or 0
    
    # Procedimentos por tipo (top 5)
    tipos_mais_realizados = (
        db.query(
            TipoProcedimento.nome,
            func.count(Procedimento.id).label('total')
        )
        .join(Procedimento)
        .group_by(TipoProcedimento.nome)
        .order_by(func.count(Procedimento.id).desc())
        .limit(5)
        .all()
    )
    
    return {
        "total_procedimentos": total_procedimentos,
        "valor_total": float(valor_total),
        "tipos_mais_realizados": [
            {"tipo": nome, "total": total}
            for nome, total in tipos_mais_realizados
        ]
    }