from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sqlalchemy import select

from app.database import get_session
from app.exceptions import NotFoundError
from app.middleware.auth import require_auth
from app.models import Account, Payment, User

user_bp = Blueprint("user", url_prefix="/user")


@user_bp.get("/me")
@require_auth
async def get_me(request: Request):
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.id == request.ctx.user_id))

    if not user:
        raise NotFoundError("User not found")

    return json({"id": user.id, "email": user.email, "full_name": user.full_name})


@user_bp.get("/accounts")
@require_auth
async def get_accounts(request: Request):
    async with get_session() as session:
        result = await session.execute(
            select(Account).where(Account.user_id == request.ctx.user_id)
        )
        accounts = result.scalars().all()

    return json(
        [
            {
                "id": a.id,
                "balance": str(a.balance),
                "created_at": a.created_at.isoformat(),
            }
            for a in accounts
        ]
    )


@user_bp.get("/payments")
@require_auth
async def get_payments(request: Request):
    async with get_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.user_id == request.ctx.user_id)
        )
        payments = result.scalars().all()

    return json(
        [
            {
                "id": p.id,
                "transaction_id": p.transaction_id,
                "account_id": p.account_id,
                "amount": str(p.amount),
                "created_at": p.created_at.isoformat(),
            }
            for p in payments
        ]
    )
