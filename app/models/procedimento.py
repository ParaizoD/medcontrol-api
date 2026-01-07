from sqlalchemy import Column, Date, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Procedimento(Base):
    __tablename__ = "procedimentos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(Date, nullable=False, index=True)
    tipo_id = Column(UUID(as_uuid=True), ForeignKey('tipos_procedimento.id'), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey('medicos.id'), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey('pacientes.id'), nullable=False, index=True)
    observacoes = Column(Text)
    valor = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (para facilitar queries depois)
    tipo = relationship("TipoProcedimento")
    medico = relationship("Medico")
    paciente = relationship("Paciente")
    
    def __repr__(self):
        return f"<Procedimento {self.id} - {self.data}>"
