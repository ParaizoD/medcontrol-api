from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False, index=True)
    cpf = Column(String(14), index=True)
    data_nascimento = Column(Date)
    telefone = Column(String(20))
    email = Column(String(255))
    endereco = Column(Text)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Paciente {self.nome}>"
