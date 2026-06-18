from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MaterialBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    descricao: str | None = None
    unidade_medida: str = Field(..., min_length=1, max_length=20)
    estoque_minimo: Decimal = Field(..., ge=0)
    preco_medio: Decimal = Field(...)
    ativo: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator("nome", "unidade_medida")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Campo obrigatorio.")
        return cleaned

    @field_validator("descricao")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("preco_medio")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Preco deve ser positivo.")
        return value


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = None
    unidade_medida: str | None = Field(default=None, min_length=1, max_length=20)
    estoque_minimo: Decimal | None = Field(default=None, ge=0)
    preco_medio: Decimal | None = None
    ativo: bool | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("nome", "unidade_medida")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Campo obrigatorio.")
        return cleaned

    @field_validator("descricao")
    @classmethod
    def clean_optional_description(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("preco_medio")
    @classmethod
    def validate_optional_price(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value <= 0:
            raise ValueError("Preco deve ser positivo.")
        return value


class MaterialResponse(MaterialBase):
    id: int


class MaterialListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[MaterialResponse]
