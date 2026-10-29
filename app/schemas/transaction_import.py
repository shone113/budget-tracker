import datetime

from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionType
from app.schemas.transaction import Amount, Description


class TransactionImportRow(BaseModel):
    type: TransactionType
    amount: Amount
    date: datetime.date
    description: Description | None = None
    category: str

    @field_validator("description", mode="before")
    @classmethod
    def empty_description_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Category is required.")
        return value


class ImportRowError(BaseModel):
    row: int
    errors: list[str]


class TransactionImportResponse(BaseModel):
    imported: int
    failed: list[ImportRowError]