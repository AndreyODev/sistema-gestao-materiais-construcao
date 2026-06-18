from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fornecedor import Fornecedor


class FornecedorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Fornecedor:
        fornecedor = Fornecedor(**data)
        self.db.add(fornecedor)
        self.db.flush()
        self.db.refresh(fornecedor)
        return fornecedor

    def get_by_id(self, fornecedor_id: int) -> Fornecedor | None:
        return self.db.get(Fornecedor, fornecedor_id)

    def get_by_cnpj(self, cnpj: str) -> Fornecedor | None:
        stmt = select(Fornecedor).where(Fornecedor.cnpj == cnpj)
        return self.db.scalar(stmt)

    def list(self) -> list[Fornecedor]:
        stmt = select(Fornecedor).order_by(Fornecedor.id)
        return list(self.db.scalars(stmt).all())

    def update(self, fornecedor: Fornecedor, data: dict) -> Fornecedor:
        for key, value in data.items():
            setattr(fornecedor, key, value)
        self.db.flush()
        self.db.refresh(fornecedor)
        return fornecedor

    def delete(self, fornecedor: Fornecedor) -> None:
        self.db.delete(fornecedor)
        self.db.flush()
