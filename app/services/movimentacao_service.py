from sqlalchemy.orm import Session

from app.models.movimentacao import TipoMovimentacao
from app.repositories.movimentacao_repository import MovimentacaoRepository


class MovimentacaoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.movimentacoes = MovimentacaoRepository(db)

    def list(self, material_id: int | None = None, tipo_movimentacao: TipoMovimentacao | None = None):
        return self.movimentacoes.list(material_id=material_id, tipo_movimentacao=tipo_movimentacao)
