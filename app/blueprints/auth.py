from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sqlalchemy import select

from app.database import get_session
from app.exceptions import AuthenticationError
from app.models import User
from app.utils.jwt_utils import create_access_token
from app.utils.password import verify_password

auth_bp = Blueprint("auth", url_prefix="/auth")


@auth_bp.post("/login")
async def login(request: Request):
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        raise AuthenticationError("Email and password are required")

    async with get_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    token = create_access_token(user.id, user.is_admin)
    return json({"access_token": token, "token_type": "bearer"})
