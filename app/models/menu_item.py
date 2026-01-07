from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)  # Nome do ícone do lucide-react
    to = Column(String(255), nullable=True)  # Path da rota
    order = Column(Integer, default=0, nullable=False)  # Ordem de exibição
    roles = Column(ARRAY(String), nullable=False, default=list)  # Lista de roles que podem ver o menu
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Hierarquia (self-referential)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=True)
    
    # Relacionamentos
    children = relationship(
        "MenuItem",
        backref="parent",
        remote_side=[id],
        cascade="all, delete",
        order_by="MenuItem.order"
    )
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MenuItem {self.label}>"
