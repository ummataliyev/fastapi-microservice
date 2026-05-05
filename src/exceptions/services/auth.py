from http import HTTPStatus

from src.exceptions.services.base import BaseServiceException


class InvalidCredentialsError(BaseServiceException):
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__("Invalid email or password")
