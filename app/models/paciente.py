from sqlalchemy import Column, String, Boolean, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"
    
    # UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dados básicos
    nome = Column(String(255), nullable=False, index=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String(20))
    email = Column(String(255))
    endereco = Column(String(500))
    
    # Controle
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    procedimentos = relationship("Procedimento", back_populates="paciente")
    
    def __repr__(self):
        return f"<Paciente {self.nome} - CPF: {self.cpf}>"
