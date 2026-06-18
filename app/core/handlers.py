from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppException


def _serialize_validation_value(value: Any) -> Any:
    if isinstance(value, Exception):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _serialize_validation_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_validation_value(item) for item in value]
    return jsonable_encoder(value)


def _normalize_validation_errors(exc: RequestValidationError) -> list[dict[str, Any]]:
    return [_serialize_validation_value(error) for error in exc.errors()]


def _resolve_validation_metadata(errors: list[dict[str, Any]]) -> tuple[str, str, dict[str, str]]:
    for error in errors:
        loc = [str(part) for part in error.get("loc", [])]
        msg = str(error.get("msg", "")).lower()
        ctx = error.get("ctx", {})
        ctx_error = str(ctx.get("error", "")).lower() if isinstance(ctx, dict) else ""
        combined_message = f"{msg} {ctx_error}"

        if "quantidade" in loc and "positiva" in combined_message:
            return (
                "INVALID_QUANTITY",
                "Quantidade deve ser positiva.",
                {"rule": "RN-004"},
            )

    return ("VALIDATION_ERROR", "Dados da requisicao invalidos.", {})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = _normalize_validation_errors(exc)
        error_code, message, metadata = _resolve_validation_metadata(errors)

        return JSONResponse(
            status_code=422,
            content={
                "error": error_code,
                "message": message,
                "details": {
                    **metadata,
                    "errors": errors,
                },
            },
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_exception(_: Request, exc: IntegrityError) -> JSONResponse:
        raw_message = str(exc.orig).lower() if exc.orig else str(exc).lower()
        if "fornecedores" in raw_message and "cnpj" in raw_message:
            error = "SUPPLIER_ALREADY_EXISTS"
            message = "Ja existe fornecedor cadastrado com este CNPJ."
            status_code = 409
        else:
            error = "DATABASE_INTEGRITY_ERROR"
            message = "Violacao de integridade de dados."
            status_code = 409

        return JSONResponse(
            status_code=status_code,
            content={"error": error, "message": message, "details": {}},
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_exception(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "DATABASE_ERROR",
                "message": "Erro interno de persistencia.",
                "details": {"reason": str(exc)},
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Erro interno inesperado.",
                "details": {"reason": str(exc)},
            },
        )
