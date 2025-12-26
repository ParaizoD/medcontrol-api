from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.procedimento import Procedimento
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.tipo_procedimento import TipoProcedimento
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Estatísticas gerais do sistema
    
    - **data_inicio**: Filtrar procedimentos a partir desta data
    - **data_fim**: Filtrar procedimentos até esta data
    """
    
    # Totais gerais
    total_medicos = db.query(func.count(Medico.id)).filter(Medico.ativo == True).scalar()
    total_pacientes = db.query(func.count(Paciente.id)).scalar()
    total_tipos = db.query(func.count(TipoProcedimento.id)).filter(TipoProcedimento.ativo == True).scalar()
    
    # Query base de procedimentos
    proc_query = db.query(Procedimento)
    
    if data_inicio:
        proc_query = proc_query.filter(Procedimento.data >= data_inicio)
    
    if data_fim:
        proc_query = proc_query.filter(Procedimento.data <= data_fim)
    
    total_procedimentos = proc_query.count()
    
    # Valor total de procedimentos
    valor_total = db.query(func.sum(Procedimento.valor)).filter(
        Procedimento.valor.isnot(None)
    ).scalar() or 0
    
    if data_inicio:
        valor_total = db.query(func.sum(Procedimento.valor)).filter(
            Procedimento.valor.isnot(None),
            Procedimento.data >= data_inicio
        ).scalar() or 0
    
    if data_fim:
        valor_total = db.query(func.sum(Procedimento.valor)).filter(
            Procedimento.valor.isnot(None),
            Procedimento.data <= data_fim
        ).scalar() or 0
    
    # Procedimentos do mês atual
    hoje = date.today()
    primeiro_dia_mes = date(hoje.year, hoje.month, 1)
    
    procedimentos_mes = db.query(func.count(Procedimento.id)).filter(
        Procedimento.data >= primeiro_dia_mes
    ).scalar()
    
    # Top 5 médicos (mais procedimentos)
    top_medicos = db.query(
        Medico.id,
        Medico.nome,
        func.count(Procedimento.id).label('total')
    ).join(
        Procedimento, Medico.id == Procedimento.medico_id
    ).group_by(
        Medico.id, Medico.nome
    ).order_by(
        func.count(Procedimento.id).desc()
    ).limit(5).all()
    
    # Top 5 tipos de procedimento
    top_tipos = db.query(
        TipoProcedimento.id,
        TipoProcedimento.nome,
        func.count(Procedimento.id).label('total')
    ).join(
        Procedimento, TipoProcedimento.id == Procedimento.tipo_id
    ).group_by(
        TipoProcedimento.id, TipoProcedimento.nome
    ).order_by(
        func.count(Procedimento.id).desc()
    ).limit(5).all()
    
    # Procedimentos por mês (últimos 6 meses)
    seis_meses_atras = hoje - timedelta(days=180)
    
    procedimentos_por_mes = db.query(
        extract('year', Procedimento.data).label('ano'),
        extract('month', Procedimento.data).label('mes'),
        func.count(Procedimento.id).label('total')
    ).filter(
        Procedimento.data >= seis_meses_atras
    ).group_by(
        extract('year', Procedimento.data),
        extract('month', Procedimento.data)
    ).order_by(
        extract('year', Procedimento.data),
        extract('month', Procedimento.data)
    ).all()
    
    # Últimos 10 procedimentos
    ultimos_procedimentos = db.query(Procedimento).order_by(
        Procedimento.data.desc()
    ).limit(10).all()
    
    return {
        "totais": {
            "medicos": total_medicos,
            "pacientes": total_pacientes,
            "tipos_procedimento": total_tipos,
            "procedimentos": total_procedimentos,
            "procedimentos_mes_atual": procedimentos_mes,
            "valor_total": float(valor_total)
        },
        "top_medicos": [
            {
                "id": str(m.id),
                "nome": m.nome,
                "total_procedimentos": m.total
            }
            for m in top_medicos
        ],
        "top_tipos": [
            {
                "id": str(t.id),
                "nome": t.nome,
                "total": t.total
            }
            for t in top_tipos
        ],
        "procedimentos_por_mes": [
            {
                "ano": int(p.ano),
                "mes": int(p.mes),
                "total": p.total
            }
            for p in procedimentos_por_mes
        ],
        "ultimos_procedimentos": [
            {
                "id": str(p.id),
                "data": p.data.isoformat(),
                "tipo": p.tipo.nome,
                "medico": p.medico.nome,
                "paciente": p.paciente.nome,
                "valor": float(p.valor) if p.valor else None
            }
            for p in ultimos_procedimentos
        ]
    }


@router.get("/relatorio-mensal")
def relatorio_mensal(
    ano: int = Query(..., ge=2020, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Relatório detalhado de um mês específico
    """
    
    # Procedimentos do mês
    procedimentos = db.query(Procedimento).filter(
        extract('year', Procedimento.data) == ano,
        extract('month', Procedimento.data) == mes
    ).all()
    
    total_procedimentos = len(procedimentos)
    valor_total = sum(float(p.valor) if p.valor else 0 for p in procedimentos)
    
    # Agrupar por tipo
    por_tipo = {}
    for p in procedimentos:
        tipo_nome = p.tipo.nome
        if tipo_nome not in por_tipo:
            por_tipo[tipo_nome] = {"quantidade": 0, "valor": 0}
        por_tipo[tipo_nome]["quantidade"] += 1
        por_tipo[tipo_nome]["valor"] += float(p.valor) if p.valor else 0
    
    # Agrupar por médico
    por_medico = {}
    for p in procedimentos:
        medico_nome = p.medico.nome
        if medico_nome not in por_medico:
            por_medico[medico_nome] = {"quantidade": 0, "valor": 0}
        por_medico[medico_nome]["quantidade"] += 1
        por_medico[medico_nome]["valor"] += float(p.valor) if p.valor else 0
    
    return {
        "periodo": {
            "ano": ano,
            "mes": mes
        },
        "resumo": {
            "total_procedimentos": total_procedimentos,
            "valor_total": valor_total
        },
        "por_tipo": [
            {"tipo": tipo, "quantidade": dados["quantidade"], "valor": dados["valor"]}
            for tipo, dados in por_tipo.items()
        ],
        "por_medico": [
            {"medico": medico, "quantidade": dados["quantidade"], "valor": dados["valor"]}
            for medico, dados in por_medico.items()
        ]
    }
