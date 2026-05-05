from http import HTTPStatus


class BaseServiceException(Exception):
    """Root for all service-layer exceptions. Routers map these to HTTPException."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Service error") -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(BaseServiceException):
    status_code = HTTPStatus.NOT_FOUND


class AlreadyExistsError(BaseServiceException):
    status_code = HTTPStatus.CONFLICT


class ValidationError(BaseServiceException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY


class PermissionDeniedError(BaseServiceException):
    status_code = HTTPStatus.FORBIDDEN


class UnauthorizedError(BaseServiceException):
    status_code = HTTPStatus.UNAUTHORIZED
