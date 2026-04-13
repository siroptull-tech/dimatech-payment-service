from sanic import Sanic
from sanic.request import Request
from sanic.response import json as json_response

from app.blueprints import admin_bp, auth_bp, user_bp, webhook_bp
from app.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)

app = Sanic("PaymentAPI")

app.blueprint(auth_bp)
app.blueprint(user_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)


@app.exception(AuthenticationError)
async def handle_authentication_error(request: Request, exc: AuthenticationError):
    return json_response({"error": str(exc)}, status=exc.status_code)


@app.exception(AuthorizationError)
async def handle_authorization_error(request: Request, exc: AuthorizationError):
    return json_response({"error": str(exc)}, status=exc.status_code)


@app.exception(NotFoundError)
async def handle_not_found(request: Request, exc: NotFoundError):
    return json_response({"error": str(exc)}, status=exc.status_code)


@app.exception(ConflictError)
async def handle_conflict(request: Request, exc: ConflictError):
    return json_response({"error": str(exc)}, status=exc.status_code)


@app.exception(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError):
    return json_response({"error": str(exc)}, status=exc.status_code)


@app.get("/health")
async def health(request: Request):
    return json_response({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, single_process=True, debug=False)
