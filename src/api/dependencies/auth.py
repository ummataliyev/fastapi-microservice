from typing import Annotated

from fastapi import Depends, Header

from src.exceptions.services.base import UnauthorizedError
from src.security.implementations.jwt import jwt_handler


def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1]
    return jwt_handler.decode(token)


CurrentUserDep = Annotated[dict, Depends(get_current_user)]
