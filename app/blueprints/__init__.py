from app.blueprints.auth import auth_bp
from app.blueprints.user import user_bp
from app.blueprints.admin import admin_bp
from app.blueprints.webhook import webhook_bp

__all__ = ["auth_bp", "user_bp", "admin_bp", "webhook_bp"]
