import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

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