from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    color: Mapped[str] = mapped_column(String(7))


Index("uq_categories_name_lower", func.lower(Category.name), unique=True)