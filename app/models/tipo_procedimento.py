from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class TipoProcedimento(Base):
    __tablename__ = "tipos_procedimento"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False, unique=True, index=True)
    descricao = Column(Text)
    valor_referencia = Column(Numeric(10, 2), default=0.00)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    procedimentos = relationship("Procedimento", back_populates="tipo")

    def __repr__(self):
        return f"<TipoProcedimento {self.nome}>"
