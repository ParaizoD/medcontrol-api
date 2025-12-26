from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict

from app.database import get_db
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.tipo_procedimento import TipoProcedimento
from app.models.procedimento import Procedimento
from app.schemas.import_schema import ImportRequest, ImportResult, ImportRow
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/import", tags=["import"])


def parse_date(date_str: str) -> datetime.date:
    """Converte string de data para date object"""
    # Tentar formato ISO (YYYY-MM-DD)
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    
    # Tentar formato brasileiro (DD/MM/YYYY)
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"Formato de data inválido: {date_str}. Use YYYY-MM-DD ou DD/MM/YYYY")


def normalize_name(name: str) -> str:
    """Normaliza nome para comparação"""
    return name.strip().lower()


def get_or_create_medico(db: Session, nome: str) -> Medico:
    """Busca médico por nome ou cria se não existir"""
    nome_normalizado = normalize_name(nome)
    
    # Buscar médico existente (case-insensitive)
    medico = db.query(Medico).filter(
        Medico.nome.ilike(nome.strip())
    ).first()
    
    if medico:
        return medico
    
    # Criar novo médico
    medico = Medico(
        nome=nome.strip(),
        crm=None,  # Será preenchido manualmente depois
        especialidade="A definir",
        ativo=True
    )
    db.add(medico)
    db.flush()  # Flush para obter o ID sem commit
    
    return medico


def get_or_create_paciente(db: Session, nome: str) -> Paciente:
    """Busca paciente por nome ou cria se não existir"""
    nome_normalizado = normalize_name(nome)
    
    # Buscar paciente existente (case-insensitive)
    paciente = db.query(Paciente).filter(
        Paciente.nome.ilike(nome.strip())
    ).first()
    
    if paciente:
        return paciente
    
    # Criar novo paciente
    paciente = Paciente(
        nome=nome.strip(),
        cpf=None,
        data_nascimento=None
    )
    db.add(paciente)
    db.flush()
    
    return paciente


def get_or_create_tipo(db: Session, nome: str) -> TipoProcedimento:
    """Busca tipo de procedimento por nome ou cria se não existir"""
    nome_normalizado = normalize_name(nome)
    
    # Buscar tipo existente (case-insensitive)
    tipo = db.query(TipoProcedimento).filter(
        TipoProcedimento.nome.ilike(nome.strip())
    ).first()
    
    if tipo:
        return tipo
    
    # Criar novo tipo
    tipo = TipoProcedimento(
        nome=nome.strip(),
        descricao="Criado automaticamente via importação",
        valor_referencia=0.00,
        ativo=True
    )
    db.add(tipo)
    db.flush()
    
    return tipo


@router.post("/procedimentos", response_model=ImportResult)
def import_procedimentos(
    data: ImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importa procedimentos em lote a partir de dados CSV
    
    Para cada linha:
    - Cria médico se não existir (por nome)
    - Cria paciente se não existir (por nome)
    - Cria tipo de procedimento se não existir (por nome)
    - Cria o procedimento
    
    Retorna estatísticas de importação
    """
    
    errors = []
    success_count = 0
    
    # Contadores de entidades criadas
    medicos_criados = set()
    pacientes_criados = set()
    tipos_criados = set()
    
    # Processar cada linha
    for idx, row in enumerate(data.rows, start=1):
        try:
            # Validar dados obrigatórios
            if not row.data:
                errors.append({"row": idx, "message": "Data é obrigatória"})
                continue
            
            if not row.nomeProcedimento:
                errors.append({"row": idx, "message": "Nome do procedimento é obrigatório"})
                continue
            
            if not row.nomeMedicos:
                errors.append({"row": idx, "message": "Nome do médico é obrigatório"})
                continue
            
            if not row.nomePaciente:
                errors.append({"row": idx, "message": "Nome do paciente é obrigatório"})
                continue
            
            # Converter data
            try:
                data_procedimento = parse_date(row.data)
            except ValueError as e:
                errors.append({"row": idx, "message": str(e)})
                continue
            
            # Buscar ou criar médico
            medico = get_or_create_medico(db, row.nomeMedicos)
            if str(medico.id) not in [str(m.id) for m in db.new]:
                # Se foi criado agora, adicionar ao contador
                if medico.created_at and (datetime.utcnow() - medico.created_at).seconds < 5:
                    medicos_criados.add(str(medico.id))
            else:
                medicos_criados.add(str(medico.id))
            
            # Buscar ou criar paciente
            paciente = get_or_create_paciente(db, row.nomePaciente)
            if str(paciente.id) not in [str(p.id) for p in db.new]:
                if paciente.created_at and (datetime.utcnow() - paciente.created_at).seconds < 5:
                    pacientes_criados.add(str(paciente.id))
            else:
                pacientes_criados.add(str(paciente.id))
            
            # Buscar ou criar tipo
            tipo = get_or_create_tipo(db, row.nomeProcedimento)
            if str(tipo.id) not in [str(t.id) for t in db.new]:
                if tipo.created_at and (datetime.utcnow() - tipo.created_at).seconds < 5:
                    tipos_criados.add(str(tipo.id))
            else:
                tipos_criados.add(str(tipo.id))
            
            # Criar procedimento
            procedimento = Procedimento(
                data=data_procedimento,
                tipo_id=tipo.id,
                medico_id=medico.id,
                paciente_id=paciente.id,
                valor=tipo.valor_referencia if tipo.valor_referencia else None,
                observacoes=None
            )
            db.add(procedimento)
            success_count += 1
            
        except Exception as e:
            errors.append({"row": idx, "message": f"Erro inesperado: {str(e)}"})
            continue
    
    # Commit de tudo de uma vez
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar no banco de dados: {str(e)}"
        )
    
    # Preparar warnings
    warnings = []
    if len(medicos_criados) > 0:
        warnings.append(
            f"{len(medicos_criados)} médico(s) foram criados automaticamente. "
            "Edite os registros para adicionar CRM e especialidade."
        )
    if len(pacientes_criados) > 0:
        warnings.append(
            f"{len(pacientes_criados)} paciente(s) foram criados automaticamente. "
            "Complete os dados cadastrais (CPF, telefone, etc)."
        )
    if len(tipos_criados) > 0:
        warnings.append(
            f"{len(tipos_criados)} tipo(s) de procedimento foram criados. "
            "Configure os valores de referência."
        )
    
    # Retornar resultado
    return ImportResult(
        success=success_count,
        errors=errors,
        created={
            "medicos": len(medicos_criados),
            "pacientes": len(pacientes_criados),
            "tiposProcedimento": len(tipos_criados),
            "procedimentos": success_count
        },
        warnings=warnings
    )
