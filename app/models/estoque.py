from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Estoque(Base):
    __tablename__ = "estoques"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materiais.id", ondelete="CASCADE"), nullable=False, unique=True)
    quantidade_disponivel: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    ultima_movimentacao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    material = relationship("Material", back_populates="estoque")
