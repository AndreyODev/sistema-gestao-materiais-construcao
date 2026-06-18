from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundException
from app.models.item_pedido import ItemPedido
from app.models.movimentacao import TipoMovimentacao
from app.models.pedido import StatusPedido
from app.repositories.estoque_repository import EstoqueRepository
from app.repositories.fornecedor_repository import FornecedorRepository
from app.repositories.material_repository import MaterialRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.repositories.pedido_repository import PedidoRepository
from app.schemas.pedido import ItemPedidoCreate, PedidoCompraCreate, PedidoCompraUpdate


class PedidoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.pedidos = PedidoRepository(db)
        self.fornecedores = FornecedorRepository(db)
        self.materiais = MaterialRepository(db)
        self.estoques = EstoqueRepository(db)
        self.movimentacoes = MovimentacaoRepository(db)

    def _get_pedido(self, pedido_id: int):
        pedido = self.pedidos.get_by_id(pedido_id)
        if pedido is None:
            raise NotFoundException("Pedido", pedido_id)
        return pedido

    def _ensure_fornecedor_exists(self, fornecedor_id: int) -> None:
        if self.fornecedores.get_by_id(fornecedor_id) is None:
            raise NotFoundException("Fornecedor", fornecedor_id)

    def _ensure_material_exists(self, material_id: int) -> None:
        if self.materiais.get_by_id(material_id) is None:
            raise NotFoundException("Material", material_id)

    def _ensure_editable(self, pedido) -> None:
        if pedido.status != StatusPedido.RASCUNHO:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Apenas pedidos em rascunho podem ser alterados.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )

    def _recalculate_total(self, pedido) -> None:
        pedido.valor_total = sum((item.subtotal for item in pedido.itens), Decimal("0.00"))
        self.db.flush()

    def create(self, payload: PedidoCompraCreate):
        self._ensure_fornecedor_exists(payload.fornecedor_id)
        try:
            pedido = self.pedidos.create(
                {
                    "fornecedor_id": payload.fornecedor_id,
                    "observacao": payload.observacao,
                    "status": StatusPedido.RASCUNHO,
                    "valor_total": Decimal("0.00"),
                }
            )
            self.db.commit()
            return self._get_pedido(pedido.id)
        except Exception:
            self.db.rollback()
            raise

    def list(self, status: StatusPedido | None, fornecedor_id: int | None):
        return self.pedidos.list(status=status, fornecedor_id=fornecedor_id)

    def get(self, pedido_id: int):
        return self._get_pedido(pedido_id)

    def update(self, pedido_id: int, payload: PedidoCompraUpdate):
        pedido = self._get_pedido(pedido_id)
        self._ensure_editable(pedido)
        data = payload.model_dump(exclude_none=True)
        if "fornecedor_id" in data:
            self._ensure_fornecedor_exists(data["fornecedor_id"])
        try:
            pedido = self.pedidos.update(pedido, data)
            self.db.commit()
            return self._get_pedido(pedido.id)
        except Exception:
            self.db.rollback()
            raise

    def delete(self, pedido_id: int) -> None:
        pedido = self._get_pedido(pedido_id)
        self._ensure_editable(pedido)
        try:
            self.pedidos.delete(pedido)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def add_item(self, pedido_id: int, payload: ItemPedidoCreate):
        pedido = self._get_pedido(pedido_id)
        self._ensure_editable(pedido)
        self._ensure_material_exists(payload.material_id)
        subtotal = payload.quantidade * payload.preco_unitario
        try:
            item = ItemPedido(
                pedido=pedido,
                material_id=payload.material_id,
                quantidade=payload.quantidade,
                preco_unitario=payload.preco_unitario,
                subtotal=subtotal,
            )
            self.pedidos.add_item(item)
            self._recalculate_total(pedido)
            self.db.commit()
            return self._get_pedido(pedido.id)
        except Exception:
            self.db.rollback()
            raise

    def approve(self, pedido_id: int):
        pedido = self._get_pedido(pedido_id)
        if pedido.status in {StatusPedido.RECEBIDO, StatusPedido.CANCELADO}:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Nao e permitido alterar pedidos em estado terminal.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )
        if pedido.status != StatusPedido.RASCUNHO:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Transicao de estado invalida para aprovacao.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )
        if not pedido.itens:
            raise AppException(
                error="ORDER_WITHOUT_ITEMS",
                message="Um pedido so pode ser aprovado se possuir pelo menos um item.",
                status_code=400,
            )
        try:
            pedido.status = StatusPedido.APROVADO
            self.db.commit()
            return self._get_pedido(pedido.id)
        except Exception:
            self.db.rollback()
            raise

    def receive(self, pedido_id: int):
        pedido = self._get_pedido(pedido_id)
        if pedido.status == StatusPedido.RECEBIDO:
            raise AppException(
                error="ORDER_ALREADY_RECEIVED",
                message="Nao e permitido receber um pedido ja recebido.",
                status_code=409,
            )
        if pedido.status == StatusPedido.CANCELADO:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Nao e permitido receber um pedido cancelado.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )
        if pedido.status != StatusPedido.APROVADO:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Somente pedidos aprovados podem ser recebidos.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )
        try:
            for item in pedido.itens:
                estoque = self.estoques.get_by_material_id(item.material_id)
                if estoque is None:
                    estoque = self.estoques.create(item.material_id)
                estoque.quantidade_disponivel += item.quantidade
                estoque.ultima_movimentacao = datetime.utcnow()
                self.movimentacoes.create(
                    {
                        "material_id": item.material_id,
                        "tipo_movimentacao": TipoMovimentacao.ENTRADA,
                        "quantidade": item.quantidade,
                        "data_movimentacao": datetime.utcnow(),
                        "observacao": f"Recebimento do pedido {pedido.id}",
                    }
                )
            pedido.status = StatusPedido.RECEBIDO
            self.db.commit()
            return self._get_pedido(pedido.id)
        except Exception as exc:
            self.db.rollback()
            raise AppException(
                error="INVALID_STOCK_UPDATE",
                message="Falha ao atualizar o estoque durante o recebimento do pedido.",
                status_code=400,
                details={"reason": str(exc)},
            ) from exc

    def cancel(self, pedido_id: int):
        pedido = self._get_pedido(pedido_id)
        if pedido.status == StatusPedido.RECEBIDO:
            raise AppException(
                error="ORDER_ALREADY_RECEIVED",
                message="Nao e permitido cancelar um pedido ja recebido.",
                status_code=409,
            )
        if pedido.status == StatusPedido.CANCELADO:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Pedido ja cancelado.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )
        if pedido.status not in {StatusPedido.RASCUNHO, StatusPedido.APROVADO}:
            raise AppException(
                error="INVALID_ORDER_STATUS_TRANSITION",
                message="Transicao de estado invalida para cancelamento.",
                status_code=409,
                details={"current_status": pedido.status.value},
            )
        try:
            pedido.status = StatusPedido.CANCELADO
            self.db.commit()
            return self._get_pedido(pedido.id)
        except Exception:
            self.db.rollback()
            raise
