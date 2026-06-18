from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.item_pedido import ItemPedido
from app.models.pedido import PedidoCompra, StatusPedido


class PedidoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> PedidoCompra:
        pedido = PedidoCompra(**data)
        self.db.add(pedido)
        self.db.flush()
        self.db.refresh(pedido)
        return pedido

    def get_by_id(self, pedido_id: int) -> PedidoCompra | None:
        stmt = (
            select(PedidoCompra)
            .options(selectinload(PedidoCompra.itens))
            .where(PedidoCompra.id == pedido_id)
        )
        return self.db.scalar(stmt)

    def list(self, status: StatusPedido | None, fornecedor_id: int | None) -> list[PedidoCompra]:
        stmt = select(PedidoCompra).options(selectinload(PedidoCompra.itens)).order_by(desc(PedidoCompra.id))
        if status is not None:
            stmt = stmt.where(PedidoCompra.status == status)
        if fornecedor_id is not None:
            stmt = stmt.where(PedidoCompra.fornecedor_id == fornecedor_id)
        return list(self.db.scalars(stmt).all())

    def update(self, pedido: PedidoCompra, data: dict) -> PedidoCompra:
        for key, value in data.items():
            setattr(pedido, key, value)
        self.db.flush()
        self.db.refresh(pedido)
        return pedido

    def delete(self, pedido: PedidoCompra) -> None:
        self.db.delete(pedido)
        self.db.flush()

    def add_item(self, item: ItemPedido) -> ItemPedido:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item
