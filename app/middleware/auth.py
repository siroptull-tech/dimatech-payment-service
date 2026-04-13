from functools import wraps

import jwt
from sanic.request import Request

from app.exceptions import AuthenticationError, AuthorizationError
from app.utils.jwt_utils import decode_access_token


def _extract_bearer_token(request: Request) -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:]
    return None


def _authenticate(request: Request) -> dict:
    token = _extract_bearer_token(request)
    if not token:
        raise AuthenticationError("Authorization header missing or malformed")
    try:
        return decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


def require_auth(f):
    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        payload = _authenticate(request)
        request.ctx.user_id = int(payload["sub"])
        request.ctx.is_admin = payload.get("is_admin", False)
        return await f(request, *args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        payload = _authenticate(request)
        request.ctx.user_id = int(payload["sub"])
        request.ctx.is_admin = payload.get("is_admin", False)
        if not request.ctx.is_admin:
            raise AuthorizationError("Admin access required")
        return await f(request, *args, **kwargs)
    return decorated
