import hashlib
import hmac

from app.config import settings

_SIGNATURE_KEYS = sorted(["account_id", "amount", "transaction_id", "user_id"])


def compute_signature(account_id, amount, transaction_id, user_id) -> str:
    values = {
        "account_id": account_id,
        "amount": amount,
        "transaction_id": transaction_id,
        "user_id": user_id,
    }
    raw = "".join(str(values[k]) for k in _SIGNATURE_KEYS) + settings.SECRET_KEY
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_webhook_signature(data: dict) -> bool:
    provided = data.get("signature")
    if not provided:
        return False

    expected = compute_signature(
        account_id=data["account_id"],
        amount=data["amount"],
        transaction_id=data["transaction_id"],
        user_id=data["user_id"],
    )
    return hmac.compare_digest(provided, expected)
