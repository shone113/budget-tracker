from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.budget import Month
from app.schemas.summary import MonthlySummaryResponse
from app.services import summary as summary_service

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("", response_model=MonthlySummaryResponse)
def get_monthly_summary(month: Annotated[Month, Query()], db: Session = Depends(get_db)):
    return summary_service.get_monthly_summary(db, month)