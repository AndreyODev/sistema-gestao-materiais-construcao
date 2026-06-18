from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.repositories.estoque_repository import EstoqueRepository
from app.repositories.material_repository import MaterialRepository
from app.schemas.material import MaterialCreate, MaterialListResponse, MaterialUpdate


class MaterialService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.materials = MaterialRepository(db)
        self.stocks = EstoqueRepository(db)

    def create(self, payload: MaterialCreate):
        try:
            material = self.materials.create(payload.model_dump())
            self.stocks.create(material.id)
            self.db.commit()
            return material
        except Exception:
            self.db.rollback()
            raise

    def list(self, nome: str | None, ativo: bool | None, limit: int, offset: int) -> MaterialListResponse:
        items, total = self.materials.list(nome=nome, ativo=ativo, limit=limit, offset=offset)
        return MaterialListResponse(total=total, limit=limit, offset=offset, items=items)

    def get(self, material_id: int):
        material = self.materials.get_by_id(material_id)
        if material is None:
            raise NotFoundException("Material", material_id)
        return material

    def update(self, material_id: int, payload: MaterialUpdate):
        material = self.get(material_id)
        try:
            updated = self.materials.update(material, payload.model_dump(exclude_none=True))
            self.db.commit()
            return updated
        except Exception:
            self.db.rollback()
            raise

    def delete(self, material_id: int) -> None:
        material = self.get(material_id)
        try:
            self.materials.delete(material)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
