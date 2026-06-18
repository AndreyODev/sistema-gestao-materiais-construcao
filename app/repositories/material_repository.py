from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.material import Material


class MaterialRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Material:
        material = Material(**data)
        self.db.add(material)
        self.db.flush()
        self.db.refresh(material)
        return material

    def get_by_id(self, material_id: int) -> Material | None:
        return self.db.get(Material, material_id)

    def list(self, nome: str | None, ativo: bool | None, limit: int, offset: int) -> tuple[list[Material], int]:
        stmt = select(Material).order_by(Material.id)
        count_stmt = select(func.count()).select_from(Material)

        if nome:
            stmt = stmt.where(Material.nome.ilike(f"%{nome}%"))
            count_stmt = count_stmt.where(Material.nome.ilike(f"%{nome}%"))
        if ativo is not None:
            stmt = stmt.where(Material.ativo == ativo)
            count_stmt = count_stmt.where(Material.ativo == ativo)

        items = list(self.db.scalars(stmt.offset(offset).limit(limit)).all())
        total = int(self.db.scalar(count_stmt) or 0)
        return items, total

    def update(self, material: Material, data: dict) -> Material:
        for key, value in data.items():
            setattr(material, key, value)
        self.db.flush()
        self.db.refresh(material)
        return material

    def delete(self, material: Material) -> None:
        self.db.delete(material)
        self.db.flush()
