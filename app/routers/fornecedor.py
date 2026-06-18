from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.fornecedor import FornecedorCreate, FornecedorResponse, FornecedorUpdate
from app.services.fornecedor_service import FornecedorService

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


@router.post("", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: FornecedorCreate, db: Session = Depends(get_db)):
    return FornecedorService(db).create(payload)


@router.get("", response_model=list[FornecedorResponse])
def list_suppliers(db: Session = Depends(get_db)):
    return FornecedorService(db).list()


@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def get_supplier(fornecedor_id: int, db: Session = Depends(get_db)):
    return FornecedorService(db).get(fornecedor_id)


@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def update_supplier(fornecedor_id: int, payload: FornecedorUpdate, db: Session = Depends(get_db)):
    return FornecedorService(db).update(fornecedor_id, payload)


@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(fornecedor_id: int, db: Session = Depends(get_db)) -> Response:
    FornecedorService(db).delete(fornecedor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
