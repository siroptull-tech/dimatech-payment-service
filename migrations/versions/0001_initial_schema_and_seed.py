"""Initial schema and seed data

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from datetime import datetime
from typing import Sequence, Union

import bcrypt
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "balance",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])


    op.create_table(
        "payments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("transaction_id", sa.String(255), nullable=False),
        sa.Column(
            "account_id",
            sa.Integer,
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_payments_transaction_id", "payments", ["transaction_id"], unique=True
    )
    op.create_index("ix_payments_account_id", "payments", ["account_id"])
    op.create_index("ix_payments_user_id", "payments", ["user_id"])


    user_hash = bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode()
    admin_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    now = datetime.utcnow()

    op.bulk_insert(
        sa.table(
            "users",
            sa.column("email", sa.String),
            sa.column("password_hash", sa.String),
            sa.column("full_name", sa.String),
            sa.column("is_admin", sa.Boolean),
            sa.column("created_at", sa.DateTime),
        ),
        [
            {
                "email": "user@example.com",
                "password_hash": user_hash,
                "full_name": "Test User",
                "is_admin": False,
                "created_at": now,
            },
            {
                "email": "admin@example.com",
                "password_hash": admin_hash,
                "full_name": "Test Admin",
                "is_admin": True,
                "created_at": now,
            },
        ],
    )

    op.execute(
        sa.text(
            "INSERT INTO accounts (user_id, balance, created_at) "
            "SELECT id, 0.00, NOW() FROM users WHERE email = 'user@example.com'"
        )
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("accounts")
    op.drop_table("users")
