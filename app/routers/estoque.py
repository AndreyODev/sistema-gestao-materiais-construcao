from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.estoque import EstoqueResponse, EstoqueSaidaRequest
from app.services.estoque_service import EstoqueService

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("/{material_id}", response_model=EstoqueResponse)
def get_stock(material_id: int, db: Session = Depends(get_db)):
    return EstoqueService(db).get(material_id)


@router.post("/saida", response_model=EstoqueResponse)
def register_output(payload: EstoqueSaidaRequest, db: Session = Depends(get_db)):
    return EstoqueService(db).register_output(payload)
