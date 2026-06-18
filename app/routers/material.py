from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material import MaterialCreate, MaterialListResponse, MaterialResponse, MaterialUpdate
from app.services.material_service import MaterialService

router = APIRouter(prefix="/materiais", tags=["Materiais"])


@router.post("", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    return MaterialService(db).create(payload)


@router.get("", response_model=MaterialListResponse)
def list_materials(
    nome: str | None = Query(default=None),
    ativo: bool | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return MaterialService(db).list(nome=nome, ativo=ativo, limit=limit, offset=offset)


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int, db: Session = Depends(get_db)):
    return MaterialService(db).get(material_id)


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(material_id: int, payload: MaterialUpdate, db: Session = Depends(get_db)):
    return MaterialService(db).update(material_id, payload)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: int, db: Session = Depends(get_db)) -> Response:
    MaterialService(db).delete(material_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
