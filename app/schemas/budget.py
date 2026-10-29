import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, field_serializer

from app.schemas.transaction import Amount


def _parse_month(value):
    if isinstance(value, datetime.date):
        return value.replace(day=1)
    if not isinstance(value, str):
        raise ValueError("Month must be in format YYYY-MM.")
    try:
        return datetime.datetime.strptime(value, "%Y-%m").date()
    except ValueError:
        raise ValueError("Month must be in format YYYY-MM.")


Month = Annotated[datetime.date, BeforeValidator(_parse_month)]


class BudgetCreateRequest(BaseModel):
    category_id: int
    month: Month
    amount: Amount


class BudgetUpdateRequest(BaseModel):
    amount: Amount


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    month: datetime.date
    amount: Decimal

    @field_serializer("month")
    def serialize_month(self, value: datetime.date) -> str:
        return value.strftime("%Y-%m")