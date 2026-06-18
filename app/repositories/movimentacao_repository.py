from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.movimentacao import MovimentacaoEstoque, TipoMovimentacao


class MovimentacaoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> MovimentacaoEstoque:
        movimentacao = MovimentacaoEstoque(**data)
        self.db.add(movimentacao)
        self.db.flush()
        self.db.refresh(movimentacao)
        return movimentacao

    def list(
        self,
        material_id: int | None = None,
        tipo_movimentacao: TipoMovimentacao | None = None,
    ) -> list[MovimentacaoEstoque]:
        stmt = select(MovimentacaoEstoque).order_by(
            desc(MovimentacaoEstoque.data_movimentacao),
            desc(MovimentacaoEstoque.id),
        )
        if material_id is not None:
            stmt = stmt.where(MovimentacaoEstoque.material_id == material_id)
        if tipo_movimentacao is not None:
            stmt = stmt.where(MovimentacaoEstoque.tipo_movimentacao == tipo_movimentacao)
        return list(self.db.scalars(stmt).all())
