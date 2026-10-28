from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.category import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest
from app.services import category as category_service

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)

@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreateRequest, db: Session = Depends(get_db)):
    return category_service.create_category(db, data)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdateRequest, db: Session = Depends(get_db)):
    return category_service.update_category(db, category_id, data)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_service.delete_category(db, category_id)