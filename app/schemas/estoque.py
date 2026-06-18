from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EstoqueResponse(BaseModel):
    id: int
    material_id: int
    quantidade_disponivel: Decimal
    ultima_movimentacao: datetime | None

    model_config = ConfigDict(from_attributes=True)


class EstoqueSaidaRequest(BaseModel):
    material_id: int = Field(..., gt=0)
    quantidade: Decimal
    observacao: str | None = None

    @field_validator("quantidade")
    @classmethod
    def validate_quantity(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Quantidade deve ser positiva.")
        return value

    @field_validator("observacao")
    @classmethod
    def clean_observation(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @model_validator(mode="after")
    def validate_payload(self) -> "EstoqueSaidaRequest":
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva.")
        return self
