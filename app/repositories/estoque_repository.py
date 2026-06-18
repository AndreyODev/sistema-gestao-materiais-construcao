from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.estoque import Estoque


class EstoqueRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_material_id(self, material_id: int) -> Estoque | None:
        stmt = select(Estoque).where(Estoque.material_id == material_id)
        return self.db.scalar(stmt)

    def create(self, material_id: int, quantidade_disponivel: Decimal = Decimal("0.00")) -> Estoque:
        estoque = Estoque(material_id=material_id, quantidade_disponivel=quantidade_disponivel)
        self.db.add(estoque)
        self.db.flush()
        self.db.refresh(estoque)
        return estoque

    def touch(self, estoque: Estoque) -> Estoque:
        estoque.ultima_movimentacao = datetime.utcnow()
        self.db.flush()
        self.db.refresh(estoque)
        return estoque
