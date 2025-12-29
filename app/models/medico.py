# app/models/medico.py

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Medico(Base):
    __tablename__ = "medicos"
    
    # UUID (mantém sua estrutura)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dados básicos
    nome = Column(String(255), nullable=False, index=True)
    crm = Column(String(50), unique=True, nullable=False, index=True)  
    especialidade = Column(String(100), nullable=False)
    email = Column(String(255))
    telefone = Column(String(20))
    
    # Controle
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Timestamps (mantém sua estrutura)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Procedimentos (NOVO)
    procedimentos = relationship("Procedimento", back_populates="medico")
    
    def __repr__(self):
        return f"<Medico {self.nome} - CRM: {self.crm}>"
