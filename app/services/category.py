from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select  

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Category
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise NotFoundError(f"Category with id {category_id} does not exist.")
    return category


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))

def create_category(db: Session, data: CategoryCreateRequest) -> Category:
    category = Category(**data.model_dump())
    db.add(category)
    _save(db, category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdateRequest) -> Category:
    category = get_category(db, category_id)

    if data.name is not None:
        category.name = data.name
    if data.color is not None:
        category.color = data.color
    
    _save(db, category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    name = category.name
    db.delete(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(f"Category '{name}' has transactions and cannot be deleted.")


def _save(db: Session, category: Category) -> None:
    name = category.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(f"Category '{name}' already exists.")
    db.refresh(category)