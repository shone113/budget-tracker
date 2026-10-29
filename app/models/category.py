from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

from app.models.budget import Budget

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    color: Mapped[str] = mapped_column(String(7))

    budgets: Mapped[list["Budget"]] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

Index("uq_categories_name_lower", func.lower(Category.name), unique=True)