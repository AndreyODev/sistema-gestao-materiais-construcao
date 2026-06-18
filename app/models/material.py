from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Material(Base):
    __tablename__ = "materiais"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    descricao: Mapped[str | None] = mapped_column(Text(), nullable=True)
    unidade_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    estoque_minimo: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    preco_medio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    itens_pedido = relationship("ItemPedido", back_populates="material")
    estoque = relationship(
        "Estoque",
        back_populates="material",
        uselist=False,
        cascade="all, delete-orphan",
    )
    movimentacoes = relationship(
        "MovimentacaoEstoque",
        back_populates="material",
        cascade="all, delete-orphan",
    )
