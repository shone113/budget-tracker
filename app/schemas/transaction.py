import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.models.transaction import TransactionType

Amount = Annotated[Decimal, Field(gt=0, le=1_000_000, decimal_places=2)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]


class TransactionCreateRequest(BaseModel):
    type: TransactionType
    amount: Amount
    date: datetime.date
    description: Description | None = None
    category_id: int


class TransactionUpdateRequest(BaseModel):
    type: TransactionType | None = None
    amount: Amount | None = None
    date: datetime.date | None = None
    description: Description | None = None
    category_id: int | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TransactionType
    amount: Decimal
    date: datetime.date
    description: str | None
    category_id: int

class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int

class TransactionFilters(BaseModel):
    date_from: datetime.date | None = None
    date_to: datetime.date | None = None
    category_id: int | None = None
    type: TransactionType | None = None
    search: str | None = Field(None, max_length=200)

    @model_validator(mode="after")
    def check_date_range(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to.")
        return self
