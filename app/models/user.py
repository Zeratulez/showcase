from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.item import Item

class User(Base):
    """
    SQLAlchemy model for user
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    username: Mapped[str] = mapped_column(String(30))
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    items: Mapped[list["Item"]] = relationship(
        "app.models.item.Item",
        back_populates="user"
    )

    __table_args__ = (
        Index("username_id_index", "id", "username"),
    )