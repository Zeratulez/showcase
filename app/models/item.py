from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class Item(Base):
    """
    SQLAlchemy model for Item
    """
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None]
    price: Mapped[float]
    tax: Mapped[float | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(
        "app.models.user.User",
        back_populates="items"
    )

    __table_args__ = (
        Index("id_name_owner_index", "id", "name", "owner_id"),
        CheckConstraint("price >= 0", name="check_price_positive"),
    )
    