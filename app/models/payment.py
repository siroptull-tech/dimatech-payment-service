from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="payments")
    account: Mapped["Account"] = relationship("Account", back_populates="payments")
