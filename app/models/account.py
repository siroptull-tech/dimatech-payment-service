from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="account", lazy="select"
    )
