from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.movimentacao import TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoResponse
from app.services.movimentacao_service import MovimentacaoService

router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


@router.get("", response_model=list[MovimentacaoResponse])
def list_movements(
    material_id: int | None = Query(default=None),
    tipo_movimentacao: TipoMovimentacao | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return MovimentacaoService(db).list(material_id=material_id, tipo_movimentacao=tipo_movimentacao)
