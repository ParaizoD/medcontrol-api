from sqlalchemy import Column, String, Date, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Procedimento(Base):
    __tablename__ = "procedimentos"
    
    # UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys (UUID)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("medicos.id"), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True)
    
    # Dados do procedimento
    tipo_procedimento = Column(String(200), nullable=False, index=True)
    data_procedimento = Column(Date, nullable=False, index=True)
    valor = Column(Numeric(10, 2), nullable=False)
    observacoes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    medico = relationship("Medico", back_populates="procedimentos")
    paciente = relationship("Paciente", back_populates="procedimentos")
    tipo = relationship("TipoProcedimento", back_populates="procedimentos")
    
    def __repr__(self):
        return f"<Procedimento {self.tipo_procedimento} - {self.data_procedimento}>"
