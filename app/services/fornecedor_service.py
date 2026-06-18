from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundException
from app.repositories.fornecedor_repository import FornecedorRepository
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate


class FornecedorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.fornecedores = FornecedorRepository(db)

    def _ensure_unique_cnpj(self, cnpj: str, current_id: int | None = None) -> None:
        fornecedor = self.fornecedores.get_by_cnpj(cnpj)
        if fornecedor and fornecedor.id != current_id:
            raise AppException(
                error="SUPPLIER_ALREADY_EXISTS",
                message="Ja existe fornecedor cadastrado com este CNPJ.",
                status_code=409,
            )

    def create(self, payload: FornecedorCreate):
        self._ensure_unique_cnpj(payload.cnpj)
        try:
            fornecedor = self.fornecedores.create(payload.model_dump())
            self.db.commit()
            return fornecedor
        except Exception:
            self.db.rollback()
            raise

    def list(self):
        return self.fornecedores.list()

    def get(self, fornecedor_id: int):
        fornecedor = self.fornecedores.get_by_id(fornecedor_id)
        if fornecedor is None:
            raise NotFoundException("Fornecedor", fornecedor_id)
        return fornecedor

    def update(self, fornecedor_id: int, payload: FornecedorUpdate):
        fornecedor = self.get(fornecedor_id)
        data = payload.model_dump(exclude_none=True)
        if "cnpj" in data:
            self._ensure_unique_cnpj(data["cnpj"], current_id=fornecedor_id)
        try:
            updated = self.fornecedores.update(fornecedor, data)
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def delete(self, fornecedor_id: int) -> None:
        fornecedor = self.get(fornecedor_id)
        try:
            self.fornecedores.delete(fornecedor)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
