from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.pedido import StatusPedido
from app.schemas.pedido import ItemPedidoCreate, PedidoCompraCreate, PedidoCompraResponse, PedidoCompraUpdate
from app.services.pedido_service import PedidoService

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoCompraResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: PedidoCompraCreate, db: Session = Depends(get_db)):
    return PedidoService(db).create(payload)


@router.get("", response_model=list[PedidoCompraResponse])
def list_orders(
    status_filter: StatusPedido | None = Query(default=None, alias="status"),
    fornecedor_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return PedidoService(db).list(status=status_filter, fornecedor_id=fornecedor_id)


@router.get("/{pedido_id}", response_model=PedidoCompraResponse)
def get_order(pedido_id: int, db: Session = Depends(get_db)):
    return PedidoService(db).get(pedido_id)


@router.put("/{pedido_id}", response_model=PedidoCompraResponse)
def update_order(pedido_id: int, payload: PedidoCompraUpdate, db: Session = Depends(get_db)):
    return PedidoService(db).update(pedido_id, payload)


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(pedido_id: int, db: Session = Depends(get_db)) -> Response:
    PedidoService(db).delete(pedido_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{pedido_id}/itens", response_model=PedidoCompraResponse)
def add_item_to_order(pedido_id: int, payload: ItemPedidoCreate, db: Session = Depends(get_db)):
    return PedidoService(db).add_item(pedido_id, payload)


@router.post("/{pedido_id}/aprovar", response_model=PedidoCompraResponse)
def approve_order(pedido_id: int, db: Session = Depends(get_db)):
    return PedidoService(db).approve(pedido_id)


@router.post("/{pedido_id}/receber", response_model=PedidoCompraResponse)
def receive_order(pedido_id: int, db: Session = Depends(get_db)):
    return PedidoService(db).receive(pedido_id)


@router.post("/{pedido_id}/cancelar", response_model=PedidoCompraResponse)
def cancel_order(pedido_id: int, db: Session = Depends(get_db)):
    return PedidoService(db).cancel(pedido_id)
