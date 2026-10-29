import datetime
from decimal import Decimal

from pydantic import BaseModel, field_serializer


class CategorySummary(BaseModel):
    category_id: int
    name: str
    spent: Decimal
    budget: Decimal | None
    left: Decimal | None


class MonthlySummaryResponse(BaseModel):
    month: datetime.date
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    categories: list[CategorySummary]

    @field_serializer("month")
    def serialize_month(self, value: datetime.date) -> str:
        return value.strftime("%Y-%m")