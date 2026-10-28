import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0 AND amount <= 1000000", name="ck_transactions_amount_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type", values_callable=lambda e: [m.value for m in e])
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    date: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(String(200))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )