class AppException(Exception):
    default_code = 500
    default_message = "Something went wrong..."
    default_details = {}

    def __init__(self, message: str = None,  code: int = None, details: dict = None) -> None:
        self.code = code or self.default_code
        self.message = message or self.default_message
        self.details = details or self.default_details
        super().__init__(message)


class UserNotFoundException(AppException):
    default_code = 404
    default_message = 'User Not Found!'
    pass


class AuthProviderNotFoundException(AppException):
    pass


class ValidationError(AppException):
    default_code = 400
    default_message = "Validation Error!"


class InvalidRefreshTokenError(ValidationError):
    pass


class TokenExpiredException(ValidationError):
    default_code = 401
    default_message = "Token Expired!"
    pass

class InvalidProviderError(ValidationError):
    pass
