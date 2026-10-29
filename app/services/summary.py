import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Budget, Category, Transaction
from app.models.transaction import TransactionType
from app.schemas.summary import CategorySummary, MonthlySummaryResponse

ZERO = Decimal("0.00")


def get_monthly_summary(db: Session, month: datetime.date) -> MonthlySummaryResponse:
    start = month
    end = datetime.date(month.year + month.month // 12, month.month % 12 + 1, 1)
    in_month = [Transaction.date >= start, Transaction.date < end]

    income = func.sum(Transaction.amount).filter(Transaction.type == TransactionType.INCOME)
    expense = func.sum(Transaction.amount).filter(Transaction.type == TransactionType.EXPENSE)
    total_income, total_expense = db.execute(
        select(func.coalesce(income, ZERO), func.coalesce(expense, ZERO)).where(*in_month)
    ).one()

    spent = (
        select(Transaction.category_id, func.sum(Transaction.amount).label("amount"))
        .where(*in_month, Transaction.type == TransactionType.EXPENSE)
        .group_by(Transaction.category_id)
        .subquery()
    )
    budget = select(Budget.category_id, Budget.amount).where(Budget.month == start).subquery()
    spent_amount = func.coalesce(spent.c.amount, ZERO)

    rows = db.execute(
        select(Category.id, Category.name, spent_amount, budget.c.amount)
        .outerjoin(spent, spent.c.category_id == Category.id)
        .outerjoin(budget, budget.c.category_id == Category.id)
        .where(or_(spent.c.amount.is_not(None), budget.c.amount.is_not(None)))
        .order_by(spent_amount.desc(), Category.name)
    )

    categories = [
        CategorySummary(
            category_id=category_id,
            name=name,
            spent=spent_value,
            budget=budget_value,
            left=budget_value - spent_value if budget_value is not None else None,
        )
        for category_id, name, spent_value, budget_value in rows
    ]

    return MonthlySummaryResponse(
        month=start,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        categories=categories,
    )