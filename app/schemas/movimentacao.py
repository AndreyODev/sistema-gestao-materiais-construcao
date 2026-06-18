from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.movimentacao import TipoMovimentacao


class MovimentacaoResponse(BaseModel):
    id: int
    material_id: int
    tipo_movimentacao: TipoMovimentacao
    quantidade: Decimal
    data_movimentacao: datetime
    observacao: str | None

    model_config = ConfigDict(from_attributes=True)
