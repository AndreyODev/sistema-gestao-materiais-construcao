from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.pedido import StatusPedido


class ItemPedidoCreate(BaseModel):
    material_id: int = Field(..., gt=0)
    quantidade: Decimal
    preco_unitario: Decimal

    @field_validator("quantidade")
    @classmethod
    def validate_quantity(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Quantidade deve ser positiva.")
        return value

    @field_validator("preco_unitario")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Preco deve ser positivo.")
        return value

    @model_validator(mode="after")
    def validate_subtotal(self) -> "ItemPedidoCreate":
        if self.quantidade * self.preco_unitario <= 0:
            raise ValueError("Subtotal invalido.")
        return self


class ItemPedidoResponse(BaseModel):
    id: int
    material_id: int
    quantidade: Decimal
    preco_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class PedidoCompraCreate(BaseModel):
    fornecedor_id: int = Field(..., gt=0)
    observacao: str | None = None

    @field_validator("observacao")
    @classmethod
    def clean_observacao(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class PedidoCompraUpdate(BaseModel):
    fornecedor_id: int | None = Field(default=None, gt=0)
    observacao: str | None = None

    @field_validator("observacao")
    @classmethod
    def clean_optional_observacao(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class PedidoCompraResponse(BaseModel):
    id: int
    fornecedor_id: int
    data_criacao: datetime
    valor_total: Decimal
    status: StatusPedido
    observacao: str | None
    itens: list[ItemPedidoResponse]

    model_config = ConfigDict(from_attributes=True)
