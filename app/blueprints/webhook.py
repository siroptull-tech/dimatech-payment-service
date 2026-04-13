from decimal import Decimal, InvalidOperation

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.exceptions import NotFoundError, ValidationError
from app.models import Account, Payment, User
from app.utils.signature import verify_webhook_signature

webhook_bp = Blueprint("webhook", url_prefix="/webhook")


@webhook_bp.post("/payment")
async def process_payment(request: Request):
    data = request.json or {}

    required = ("transaction_id", "account_id", "user_id", "amount", "signature")
    missing = [f for f in required if f not in data]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    if not verify_webhook_signature(data):
        return json({"error": "Invalid signature"}, status=400)

    try:
        transaction_id = str(data["transaction_id"])
        account_id = int(data["account_id"])
        user_id = int(data["user_id"])
        amount = Decimal(str(data["amount"]))
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError("Invalid field types")

    if amount <= 0:
        raise ValidationError("Amount must be a positive number")

    try:
        async with get_session() as session:
            existing_payment = await session.scalar(
                select(Payment).where(Payment.transaction_id == transaction_id)
            )
            if existing_payment:
                return json({"message": "Transaction already processed"}, status=200)

            user = await session.scalar(select(User).where(User.id == user_id))
            if not user:
                raise NotFoundError(f"User {user_id} not found")

            account = await session.scalar(
                select(Account)
                .where(Account.id == account_id, Account.user_id == user_id)
                .with_for_update()
            )

            if account is None:
                account = Account(user_id=user_id, balance=Decimal("0.00"))
                session.add(account)
                await session.flush()

            payment = Payment(
                transaction_id=transaction_id,
                account_id=account.id,
                user_id=user_id,
                amount=amount,
            )
            session.add(payment)

            account.balance = account.balance + amount

    except IntegrityError:
        return json({"message": "Transaction already processed"}, status=200)

    return json({"message": "Payment processed successfully"}, status=200)
