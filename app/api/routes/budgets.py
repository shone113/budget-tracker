from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.budget import BudgetCreateRequest, BudgetResponse, BudgetUpdateRequest, Month
from app.services import budget as budget_service

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=list[BudgetResponse])
def list_budgets(month: Annotated[Month, Query()], db: Session = Depends(get_db)):
    return budget_service.list_budgets(db, month)


@router.post("", response_model=BudgetResponse, status_code=201)
def create_budget(data: BudgetCreateRequest, db: Session = Depends(get_db)):
    return budget_service.create_budget(db, data)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, data: BudgetUpdateRequest, db: Session = Depends(get_db)):
    return budget_service.update_budget(db, budget_id, data)


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    budget_service.delete_budget(db, budget_id)