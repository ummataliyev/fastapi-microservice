import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.core.settings import settings

_basic = HTTPBasic()


def get_current_user_for_docs(
    credentials: Annotated[HTTPBasicCredentials, Depends(_basic)],
) -> str:
    user_ok = secrets.compare_digest(credentials.username, settings.docs_username)
    pass_ok = secrets.compare_digest(credentials.password, settings.docs_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
