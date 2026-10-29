class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str, details: list | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class BusinessRuleError(AppError):
    status_code = 422
    code = "business_rule_violation"