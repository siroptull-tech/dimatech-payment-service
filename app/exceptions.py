from sanic.exceptions import SanicException


class AuthenticationError(SanicException):
    status_code = 401


class AuthorizationError(SanicException):
    status_code = 403


class NotFoundError(SanicException):
    status_code = 404


class ConflictError(SanicException):
    status_code = 409


class ValidationError(SanicException):
    status_code = 422
