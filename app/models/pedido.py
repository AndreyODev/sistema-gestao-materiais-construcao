from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StatusPedido(str, Enum):
    RASCUNHO = "RASCUNHO"
    APROVADO = "APROVADO"
    RECEBIDO = "RECEBIDO"
    CANCELADO = "CANCELADO"


class PedidoCompra(Base):
    __tablename__ = "pedidos_compra"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id", ondelete="RESTRICT"), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    status: Mapped[StatusPedido] = mapped_column(
        SqlEnum(StatusPedido, name="status_pedido"),
        nullable=False,
        default=StatusPedido.RASCUNHO,
    )
    observacao: Mapped[str | None] = mapped_column(Text(), nullable=True)

    fornecedor = relationship("Fornecedor", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
