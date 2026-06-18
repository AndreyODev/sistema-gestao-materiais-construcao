from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundException
from app.models.movimentacao import TipoMovimentacao
from app.repositories.estoque_repository import EstoqueRepository
from app.repositories.material_repository import MaterialRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.schemas.estoque import EstoqueSaidaRequest


class EstoqueService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.estoques = EstoqueRepository(db)
        self.materiais = MaterialRepository(db)
        self.movimentacoes = MovimentacaoRepository(db)

    def get(self, material_id: int):
        material = self.materiais.get_by_id(material_id)
        if material is None:
            raise NotFoundException("Material", material_id)
        estoque = self.estoques.get_by_material_id(material_id)
        if estoque is None:
            estoque = self.estoques.create(material_id, Decimal("0.00"))
            self.db.commit()
        return estoque

    def register_output(self, payload: EstoqueSaidaRequest):
        material = self.materiais.get_by_id(payload.material_id)
        if material is None:
            raise NotFoundException("Material", payload.material_id)

        estoque = self.estoques.get_by_material_id(payload.material_id)
        if estoque is None:
            estoque = self.estoques.create(payload.material_id, Decimal("0.00"))

        if estoque.quantidade_disponivel < payload.quantidade:
            self.db.rollback()
            raise AppException(
                error="INSUFFICIENT_STOCK",
                message="Nao permitir movimentacao de saida que deixe o estoque negativo.",
                status_code=409,
                details={
                    "available": float(estoque.quantidade_disponivel),
                    "requested": float(payload.quantidade),
                },
            )

        try:
            estoque.quantidade_disponivel -= payload.quantidade
            estoque.ultima_movimentacao = datetime.utcnow()
            self.movimentacoes.create(
                {
                    "material_id": payload.material_id,
                    "tipo_movimentacao": TipoMovimentacao.SAIDA,
                    "quantidade": payload.quantidade,
                    "data_movimentacao": datetime.utcnow(),
                    "observacao": payload.observacao or "Saida manual de estoque",
                }
            )
            self.db.commit()
            return estoque
        except Exception:
            self.db.rollback()
            raise
