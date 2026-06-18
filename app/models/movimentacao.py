from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materiais.id", ondelete="RESTRICT"), nullable=False)
    tipo_movimentacao: Mapped[TipoMovimentacao] = mapped_column(
        SqlEnum(TipoMovimentacao, name="tipo_movimentacao"),
        nullable=False,
    )
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_movimentacao: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    observacao: Mapped[str | None] = mapped_column(Text(), nullable=True)

    material = relationship("Material", back_populates="movimentacoes")
