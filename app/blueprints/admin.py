from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.middleware.auth import require_admin
from app.models import Account, User
from app.utils.password import hash_password

admin_bp = Blueprint("admin", url_prefix="/admin")


@admin_bp.get("/me")
@require_admin
async def get_me(request: Request):
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.id == request.ctx.user_id))

    if not user:
        raise NotFoundError("User not found")

    return json({"id": user.id, "email": user.email, "full_name": user.full_name})


@admin_bp.get("/users")
@require_admin
async def get_users(request: Request):
    async with get_session() as session:
        result = await session.execute(
            select(User)
            .where(User.is_admin.is_(False))
            .options(selectinload(User.accounts))
        )
        users = result.scalars().all()

    return json(
        [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "created_at": u.created_at.isoformat(),
                "accounts": [
                    {"id": a.id, "balance": str(a.balance)}
                    for a in u.accounts
                ],
            }
            for u in users
        ]
    )


@admin_bp.post("/users")
@require_admin
async def create_user(request: Request):
    data = request.json or {}

    for field in ("email", "password", "full_name"):
        if not data.get(field):
            raise ValidationError(f"Field '{field}' is required")

    async with get_session() as session:
        existing = await session.scalar(
            select(User).where(User.email == data["email"])
        )
        if existing:
            raise ConflictError("A user with this email already exists")

        user = User(
            email=data["email"],
            password_hash=hash_password(data["password"]),
            full_name=data["full_name"],
            is_admin=bool(data.get("is_admin", False)),
        )
        session.add(user)
        await session.flush()

        return json(
            {"id": user.id, "email": user.email, "full_name": user.full_name},
            status=201,
        )


@admin_bp.put("/users/<user_id:int>")
@require_admin
async def update_user(request: Request, user_id: int):
    data = request.json or {}
    if not data:
        raise ValidationError("Request body must not be empty")

    async with get_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))
        if not user:
            raise NotFoundError("User not found")

        if "email" in data:
            collision = await session.scalar(
                select(User).where(User.email == data["email"], User.id != user_id)
            )
            if collision:
                raise ConflictError("Email is already taken")
            user.email = data["email"]

        if "full_name" in data:
            user.full_name = data["full_name"]

        if "password" in data:
            user.password_hash = hash_password(data["password"])

        return json({"id": user.id, "email": user.email, "full_name": user.full_name})


@admin_bp.delete("/users/<user_id:int>")
@require_admin
async def delete_user(request: Request, user_id: int):
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))
        if not user:
            raise NotFoundError("User not found")

        await session.delete(user)

    return json({"message": "User deleted successfully"})
