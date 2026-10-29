from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionResponse,
    TransactionUpdateRequest,
    TransactionFilters
)
from app.services import transaction as transaction_service

from fastapi import APIRouter, Depends, Query
from app.schemas.transaction import TransactionListResponse 

import datetime
from typing import Annotated
from app.models.transaction import TransactionType

from fastapi import UploadFile

from app.core.exceptions import BusinessRuleError
from app.schemas.transaction_import import TransactionImportResponse
from app.services import transaction_import as transaction_import_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/search", response_model=TransactionListResponse)
def search_transactions(
    filters: Annotated[TransactionFilters, Query()],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = transaction_service.list_transactions(db, filters, page, page_size)
    return TransactionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    return transaction_service.get_transaction(db, transaction_id)

@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(data: TransactionCreateRequest, db: Session = Depends(get_db)):
    return transaction_service.create_transaction(db, data)

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, data: TransactionUpdateRequest, db: Session = Depends(get_db)):
    return transaction_service.update_transaction(db, transaction_id, data)

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction_service.delete_transaction(db, transaction_id)

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = transaction_service.list_transactions(db, TransactionFilters(), page, page_size)
    return TransactionListResponse(items=items, total=total, page=page, page_size=page_size)

@router.post("/import", response_model=TransactionImportResponse)
def import_transactions(file: UploadFile, db: Session = Depends(get_db)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise BusinessRuleError("Only .csv files are supported.")
    return transaction_import_service.import_transactions(db, file.file)
