import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Budget, Category
from app.schemas.budget import BudgetCreateRequest, BudgetUpdateRequest

def get_budget(db: Session, budget_id: int) -> Budget:
    budget = db.get(Budget, budget_id)
    if budget is None:
        raise NotFoundError(f"Budget with id {budget_id} does not exist.")
    return budget

def list_budgets(db: Session, month: datetime.date) -> list[Budget]:
    return list(db.scalars(
        select(Budget).where(Budget.month == month).order_by(Budget.category_id)
    ))


def create_budget(db: Session, data: BudgetCreateRequest) -> Budget:
    if db.get(Category, data.category_id) is None:
        raise BusinessRuleError(f"Category with id {data.category_id} does not exist.")
    budget = Budget(**data.model_dump())
    db.add(budget)
    _save(db, budget)
    return budget


def update_budget(db: Session, budget_id: int, data: BudgetUpdateRequest) -> Budget:
    budget = get_budget(db, budget_id)
    budget.amount = data.amount
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget_id: int) -> None:
    budget = get_budget(db, budget_id)
    db.delete(budget)
    db.commit()

def _find(db: Session, category_id: int, month: datetime.date) -> Budget | None:
    return db.scalar(
        select(Budget).where(Budget.category_id == category_id, Budget.month == month)
    )


def _save(db: Session, budget: Budget) -> None:
    category_id, month = budget.category_id, budget.month
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            f"Budget for category {category_id} and month {month:%Y-%m} already exists."
        )
    db.refresh(budget)