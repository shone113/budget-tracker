from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models import Category, Transaction
from app.schemas.transaction import TransactionCreateRequest, TransactionUpdateRequest

from sqlalchemy import func, select


def get_transaction(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise NotFoundError(f"Transaction with id {transaction_id} does not exist.")
    return transaction


def list_transactions(db: Session, page: int, page_size: int) -> tuple[list[Transaction], int]:
    total = db.scalar(select(func.count()).select_from(Transaction))

    statement = (
        select(Transaction)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(statement))
    return items, total


def create_transaction(db: Session, data: TransactionCreateRequest) -> Transaction:
    _ensure_category_exists(db, data.category_id)
    transaction = Transaction(**data.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(db: Session, transaction_id: int, data: TransactionUpdateRequest) -> Transaction:
    transaction = get_transaction(db, transaction_id)

    if data.type is not None:
        transaction.type = data.type
    if data.amount is not None:
        transaction.amount = data.amount
    if data.date is not None:
        transaction.date = data.date
    if data.category_id is not None:
        _ensure_category_exists(db, data.category_id)
        transaction.category_id = data.category_id
    if "description" in data.model_fields_set:
        transaction.description = data.description

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction_id: int) -> None:
    transaction = get_transaction(db, transaction_id)
    db.delete(transaction)
    db.commit()


def _ensure_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise BusinessRuleError(f"Category with id {category_id} does not exist.")