import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class FornecedorBase(BaseModel):
    razao_social: str = Field(..., min_length=1, max_length=160)
    cnpj: str = Field(..., min_length=14, max_length=18)
    telefone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    ativo: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator("razao_social")
    @classmethod
    def validate_razao_social(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Campo obrigatorio.")
        return cleaned

    @field_validator("telefone")
    @classmethod
    def clean_phone(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) != 14:
            raise ValueError("CNPJ invalido.")
        return digits


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorUpdate(BaseModel):
    razao_social: str | None = Field(default=None, min_length=1, max_length=160)
    cnpj: str | None = Field(default=None, min_length=14, max_length=18)
    telefone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    ativo: bool | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("razao_social")
    @classmethod
    def validate_optional_razao_social(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Campo obrigatorio.")
        return cleaned

    @field_validator("telefone")
    @classmethod
    def clean_optional_phone(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("cnpj")
    @classmethod
    def validate_optional_cnpj(cls, value: str | None) -> str | None:
        if value is None:
            return value
        digits = re.sub(r"\D", "", value)
        if len(digits) != 14:
            raise ValueError("CNPJ invalido.")
        return digits


class FornecedorResponse(FornecedorBase):
    id: int
