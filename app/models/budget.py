import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("category_id", "month", name="uq_budgets_category_month"),
        CheckConstraint("amount > 0 AND amount <= 1000000", name="ck_budgets_amount_range"),
        CheckConstraint("EXTRACT(DAY FROM month) = 1", name="ck_budgets_month_first_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    month: Mapped[datetime.date] = mapped_column(Date)  
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))