# fastapi-microservice Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the contents of `github/microservices/fastapi-microservice` with a fresh skeleton derived from `safia/safia-shared/boilerplate/template_service`, plus a working auth/users example, four custom middlewares, and a refreshed CI/README — preserving the existing git history.

**Architecture:** Greenfield port. Start by copying the boilerplate verbatim into the target repo (after backup), then layer the auth/users domain on top using the boilerplate's `BaseService[TM] + TransactionManager` pattern. Add four custom middlewares ported from the old service, simplified for the new exception-handler convention.

**Tech Stack:** FastAPI 0.115+, SQLAlchemy 2.0 async, asyncpg, Alembic, Pydantic 2, PyJWT, passlib[bcrypt], fastapi-pagination, prometheus-fastapi-instrumentator, sentry-sdk, APScheduler, uv, ruff, hatchling, pytest + pytest-asyncio.

**Reference paths used throughout:**
- `BOILERPLATE` = `/Users/the_elita/Desktop/apps/safia/safia-shared/boilerplate/template_service`
- `TARGET` = `/Users/the_elita/Desktop/apps/github/microservices/fastapi-microservice`
- `SPEC` = `$TARGET/docs/superpowers/specs/2026-05-05-fastapi-microservice-migration-design.md`

The implementing engineer should `cd $TARGET` for all git/python/uv operations unless stated otherwise.

---

## Task 1: Backup branch + tag

**Files:** none (git only)

- [ ] **Step 1: Verify clean working tree**

```bash
cd /Users/the_elita/Desktop/apps/github/microservices/fastapi-microservice
git status
```

Expected: clean working tree, branch `main` (or current default).

If unclean, stop and resolve before proceeding.

- [ ] **Step 2: Tag the pre-migration HEAD**

```bash
git tag -a pre-migration -m "Snapshot of fastapi-microservice before boilerplate migration (2026-05-05)"
```

- [ ] **Step 3: Create + push backup branch**

```bash
git checkout -b pre-migration-backup
git push -u origin pre-migration-backup
git push origin pre-migration
git checkout main
```

Expected: backup branch and tag both visible on remote.

- [ ] **Step 4: Create working branch**

```bash
git checkout -b boilerplate-migration
```

---

## Task 2: Wipe and replace tree from boilerplate

**Files:** wholesale replacement of repository contents

- [ ] **Step 1: Remove caches and old src/infra/locks**

```bash
cd /Users/the_elita/Desktop/apps/github/microservices/fastapi-microservice
rm -rf src/ infra/ .pytest_cache/ .ruff_cache/ .venv/
rm -f poetry.lock pytest.ini alembic.ini Makefile makefile pyproject.toml ruff.toml
rm -f .pre-commit-config.yaml .python-version .gitignore
rm -f docs/openapi.json docs/collection.json
find . -name '.DS_Store' -delete
```

(Keep `.git/`, `.github/`, `docs/superpowers/`, `README.md`, `uv.lock` if present — `uv.lock` will be regenerated.)

```bash
rm -f uv.lock
```

- [ ] **Step 2: Copy boilerplate over**

```bash
cp -R /Users/the_elita/Desktop/apps/safia/safia-shared/boilerplate/template_service/. /Users/the_elita/Desktop/apps/github/microservices/fastapi-microservice/
```

- [ ] **Step 3: Remove `.gitea/` (target uses `.github/`)**

```bash
rm -rf .gitea/
```

- [ ] **Step 4: Verify the copy**

```bash
ls -la
ls src/
```

Expected: `src/`, `infra/`, `pyproject.toml`, `Makefile`, `alembic.ini`, `ruff.toml`, `.gitignore`, `.pre-commit-config.yaml`, `.python-version`, `uv.lock`, `README.md` all present. `.gitea/` absent.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: replace tree with boilerplate skeleton"
```

---

## Task 3: Update pyproject.toml metadata

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Replace project name**

In `pyproject.toml`, change:

```toml
[project]
name = "template-service"
```

to:

```toml
[project]
name = "fastapi-microservice"
description = "FastAPI microservice template — postgres + JWT auth + middlewares"
readme = "README.md"
```

- [ ] **Step 2: Add `email-validator` to dependencies**

In the `[project] dependencies` array, add (alphabetically):

```toml
    "email-validator>=2.2.0",
```

- [ ] **Step 3: Regenerate lock**

```bash
uv lock
```

Expected: `uv.lock` updated, no errors.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: rename project to fastapi-microservice and add email-validator"
```

---

## Task 4: Verify boilerplate JWT + alembic config (no edits)

**Files:** none

This task is a sanity check before continuing — boilerplate already provides `refresh_token_expire_days` and a wired alembic env. Confirm both before relying on them in later tasks.

- [ ] **Step 1: Confirm JWTSettings fields**

```bash
grep -E "(secret_key|algorithm|access_token|refresh_token)" src/core/jwt.py
```

Expected output includes:
```
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
```

If `refresh_token_expire_days` is missing, add it manually before continuing — later tasks reference `settings.jwt.refresh_token_expire_days`.

- [ ] **Step 2: Confirm alembic env.py imports models**

```bash
grep -E "(from src.models|target_metadata)" src/migrations/env.py
```

Expected:
```
from src.models import *  # noqa: F401,F403  -- so autogenerate sees every model
target_metadata = Base.metadata
```

If either line is missing, add it.

- [ ] **Step 3: No commit** (verification only)

---

## Task 5: Add `schemas/base.py` shared mixins

**Files:**
- Create: `src/schemas/base.py`

- [ ] **Step 1: Create the file**

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UUIDSchema(BaseModel):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Commit**

```bash
git add src/schemas/base.py
git commit -m "feat(schemas): add UUIDSchema and TimestampSchema base mixins"
```

---

## Task 6: Add `schemas/users.py`

**Files:**
- Create: `src/schemas/users.py`

- [ ] **Step 1: Create the file**

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.base import TimestampSchema, UUIDSchema


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


class UserReadSchema(UUIDSchema, TimestampSchema):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserInternalCreateSchema(BaseModel):
    email: EmailStr
    password: str  # already hashed


class UserInternalSchema(UserReadSchema):
    password: str = Field(exclude=True)
```

- [ ] **Step 2: Commit**

```bash
git add src/schemas/users.py
git commit -m "feat(schemas): add user schemas"
```

---

## Task 7: Add `schemas/auth.py`

**Files:**
- Create: `src/schemas/auth.py`

- [ ] **Step 1: Create the file**

```python
from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

- [ ] **Step 2: Commit**

```bash
git add src/schemas/auth.py
git commit -m "feat(schemas): add auth schemas (login, refresh, token response)"
```

---

## Task 8: Add `models/users.py`

**Files:**
- Create: `src/models/users.py`

- [ ] **Step 1: Create the file**

```python
from sqlalchemy import CheckConstraint, Index, String, event, text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class Users(BaseModel):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="ck_user_email_lowercase"),
        Index("uq_user_email_lower", text("lower(email)"), unique=True),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


@event.listens_for(Users, "before_insert")
@event.listens_for(Users, "before_update")
def _normalize_email(mapper, connection, target):
    if target.email:
        target.email = target.email.lower()
```

- [ ] **Step 2: Register model in `__init__.py` so alembic sees it**

Open `src/models/__init__.py`. If it's empty or only contains the `BaseModel` re-export, append:

```python
from src.models.users import Users  # noqa: F401  (registered for alembic)
```

- [ ] **Step 3: Commit**

```bash
git add src/models/users.py src/models/__init__.py
git commit -m "feat(models): add Users model with lowercased-email constraints"
```

---

## Task 9: Add `mappers/users.py`

**Files:**
- Create: `src/mappers/users.py`

- [ ] **Step 1: Create the file**

```python
from src.mappers.base import BaseDataMapper
from src.models.users import Users
from src.schemas.users import UserReadSchema


class UsersMapper(BaseDataMapper[Users, UserReadSchema]):
    model = Users
    schema = UserReadSchema
```

- [ ] **Step 2: Commit**

```bash
git add src/mappers/users.py
git commit -m "feat(mappers): add UsersMapper"
```

---

## Task 10: Add password hasher (interface + bcrypt impl)

**Files:**
- Create: `src/security/interfaces/hasher.py`
- Create: `src/security/implementations/bcrypt.py`
- Test: `src/tests/security/test_bcrypt_hasher.py`

- [ ] **Step 1: Write the failing test**

Create `src/tests/security/__init__.py` (empty) if not present. Then create `src/tests/security/test_bcrypt_hasher.py`:

```python
from src.security.implementations.bcrypt import BcryptPasswordHasher


def test_hash_then_verify_returns_true():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("hunter2-secure")
    assert hashed != "hunter2-secure"
    assert hasher.verify("hunter2-secure", hashed) is True


def test_verify_with_wrong_password_returns_false():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("hunter2-secure")
    assert hasher.verify("wrong-password", hashed) is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest src/tests/security/test_bcrypt_hasher.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.security.implementations.bcrypt'`.

- [ ] **Step 3: Create base markers in the security sub-packages**

For consistency with the rest of the codebase (every layer has `base.py`), add minimal marker files.

`src/security/interfaces/base.py`:

```python
"""Base for protocol-style security interfaces.

Each interface in this package (e.g. JWTHandler, PasswordHasher) is a
typing.Protocol. New interfaces should follow the same pattern: define a
Protocol and reference it from the matching implementation file.
"""
```

`src/security/implementations/base.py`:

```python
"""Base for security implementations.

Each module here implements one interface from `src.security.interfaces`.
Singletons (e.g. `jwt_handler`, `bcrypt_hasher`) are instantiated at the
bottom of each module so callers can import them directly.
"""
```

- [ ] **Step 4: Create the interface**

Create `src/security/interfaces/hasher.py`:

```python
from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...
```

- [ ] **Step 5: Create the bcrypt implementation**

Create `src/security/implementations/bcrypt.py`:

```python
from passlib.context import CryptContext

from src.security.interfaces.hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self._ctx.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._ctx.verify(plain, hashed)


bcrypt_hasher = BcryptPasswordHasher()
```

- [ ] **Step 6: Run test to verify it passes**

```bash
uv run pytest src/tests/security/test_bcrypt_hasher.py -v
```

Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add src/security/
git add src/tests/security/
git commit -m "feat(security): add bcrypt password hasher and base markers"
```

---

## Task 11: Add `repositories/users.py`

**Files:**
- Create: `src/repositories/users.py`

(Repo behavior is exercised end-to-end in Task 30's smoke test; unit-testing the SQL would require a fixture-heavy setup. We rely on the smoke test plus type checking here.)

- [ ] **Step 1: Create the file**

```python
from sqlalchemy import select

from src.mappers.users import UsersMapper
from src.models.users import Users
from src.repositories.base import BaseRepository
from src.schemas.users import UserInternalSchema, UserReadSchema


class UsersRepository(BaseRepository[Users, UserReadSchema]):
    model = Users
    mapper = UsersMapper
    entity_name = "User"

    async def get_by_email(self, email: str) -> UserReadSchema | None:
        stmt = self._active_filter(select(Users).where(Users.email == email))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        return self.mapper.map_to_domain_entity(instance) if instance else None

    async def get_internal_by_email(self, email: str) -> UserInternalSchema | None:
        stmt = self._active_filter(select(Users).where(Users.email == email))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        if instance is None:
            return None
        return UserInternalSchema.model_validate(instance, from_attributes=True)

    def list_select(self):
        """Public Select for pagination — applies the soft-delete filter."""
        return self._active_filter(select(Users))
```

- [ ] **Step 2: Commit**

```bash
git add src/repositories/users.py
git commit -m "feat(repositories): add UsersRepository with email lookups"
```

---

## Task 12: Wire `UsersRepository` into managers

**Files:**
- Modify: `src/managers/db/transaction.py`
- Modify: `src/managers/db/readonly.py`

- [ ] **Step 1: Update `transaction.py`**

Replace the contents of `src/managers/db/transaction.py` with:

```python
from src.managers.db.base import BaseTransactionManager
from src.repositories.users import UsersRepository


class TransactionManager(BaseTransactionManager):
    """Read/write session. Commits on clean exit, rolls back on exception."""

    users: UsersRepository

    async def __aenter__(self) -> "TransactionManager":
        await self._open_session()
        self._wire_repositories()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self._close_session(exc_type, exc_val, exc_tb)

    def _wire_repositories(self) -> None:
        self.users = UsersRepository(self.session)
```

- [ ] **Step 2: Update `readonly.py`**

Replace the contents of `src/managers/db/readonly.py` with:

```python
from src.managers.db.base import BaseTransactionManager
from src.repositories.users import UsersRepository


class ReadonlyManager(BaseTransactionManager):
    """Read-only session. Always rolls back on exit (never commits)."""

    users: UsersRepository

    async def __aenter__(self) -> "ReadonlyManager":
        await self._open_session()
        self._wire_repositories()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await self.session.rollback()
        finally:
            await self._close_session(exc_type, exc_val, exc_tb)

    def _wire_repositories(self) -> None:
        self.users = UsersRepository(self.session)
```

- [ ] **Step 3: Commit**

```bash
git add src/managers/db/transaction.py src/managers/db/readonly.py
git commit -m "feat(managers): wire UsersRepository into transaction/readonly managers"
```

---

## Task 13: Add `exceptions/services/auth.py`

**Files:**
- Create: `src/exceptions/services/auth.py`

- [ ] **Step 1: Create the file**

```python
from http import HTTPStatus

from src.exceptions.services.base import BaseServiceException


class InvalidCredentialsError(BaseServiceException):
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__("Invalid email or password")
```

- [ ] **Step 2: Commit**

```bash
git add src/exceptions/services/auth.py
git commit -m "feat(exceptions): add InvalidCredentialsError"
```

---

## Task 14: Add `services/users.py`

**Files:**
- Create: `src/services/users.py`

- [ ] **Step 1: Create the file**

```python
from uuid import UUID

from fastapi_pagination import Page
from sqlalchemy import select

from src.managers.db.transaction import TransactionManager
from src.mappers.users import UsersMapper
from src.models.users import Users
from src.schemas.users import (
    UserCreateSchema,
    UserInternalCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from src.security.implementations.bcrypt import bcrypt_hasher
from src.services.base import BaseService


class UsersService(BaseService[TransactionManager]):
    hasher = bcrypt_hasher

    async def list(self) -> Page[UserReadSchema]:
        stmt = self.db.users.list_select().order_by(Users.created_at.desc())
        return await self.paginated_list(
            stmt,
            transformer=lambda rows: [UsersMapper.map_to_domain_entity(r) for r in rows],
        )

    async def get(self, user_id: UUID) -> UserReadSchema:
        return await self.db.users.get_one(user_id)

    async def create(self, data: UserCreateSchema) -> UserReadSchema:
        email = data.email.lower()
        hashed = self.hasher.hash(data.password)
        return await self.db.users.create(
            UserInternalCreateSchema(email=email, password=hashed)
        )

    async def update(self, user_id: UUID, data: UserUpdateSchema) -> UserReadSchema:
        payload = data.model_dump(exclude_unset=True)
        if "password" in payload and payload["password"] is not None:
            payload["password"] = self.hasher.hash(payload["password"])
        if "email" in payload and payload["email"] is not None:
            payload["email"] = payload["email"].lower()
        return await self.db.users.update(user_id, payload)

    async def delete(self, user_id: UUID) -> None:
        await self.db.users.soft_delete(user_id)
```

- [ ] **Step 2: Commit**

```bash
git add src/services/users.py
git commit -m "feat(services): add UsersService"
```

---

## Task 15: Add `services/auth.py`

**Files:**
- Create: `src/services/auth.py`
- Test: `src/tests/services/test_auth_service_tokens.py`

- [ ] **Step 1: Write a focused unit test for token issuance**

Create `src/tests/services/__init__.py` (empty) if absent, then `src/tests/services/test_auth_service_tokens.py`:

```python
from datetime import datetime, timezone
from uuid import uuid4

import jwt as pyjwt

from src.core.settings import settings
from src.schemas.users import UserReadSchema
from src.services.auth import AuthService


def _make_user() -> UserReadSchema:
    now = datetime.now(timezone.utc)
    return UserReadSchema(
        id=uuid4(),
        created_at=now,
        updated_at=now,
        email="alice@example.com",
    )


def test_issue_tokens_returns_decodable_access_and_refresh():
    user = _make_user()
    service = AuthService(db=None)  # _issue_tokens does not touch self.db

    tokens = service._issue_tokens(user)

    access = pyjwt.decode(
        tokens.access_token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )
    refresh = pyjwt.decode(
        tokens.refresh_token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )

    assert access["sub"] == str(user.id)
    assert access["type"] == "access"
    assert refresh["sub"] == str(user.id)
    assert refresh["type"] == "refresh"
    assert tokens.token_type == "bearer"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest src/tests/services/test_auth_service_tokens.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.services.auth'`.

- [ ] **Step 3: Create the service**

Create `src/services/auth.py`:

```python
from uuid import UUID

from src.core.settings import settings
from src.exceptions.repositories.base import EntityNotFoundError
from src.exceptions.services.auth import InvalidCredentialsError
from src.exceptions.services.base import AlreadyExistsError, UnauthorizedError
from src.managers.db.transaction import TransactionManager
from src.schemas.auth import LoginSchema, TokenResponseSchema
from src.schemas.users import (
    UserCreateSchema,
    UserInternalCreateSchema,
    UserReadSchema,
)
from src.security.implementations.bcrypt import bcrypt_hasher
from src.security.implementations.jwt import jwt_handler
from src.services.base import BaseService


class AuthService(BaseService[TransactionManager]):
    jwt = jwt_handler
    hasher = bcrypt_hasher

    async def register(self, data: UserCreateSchema) -> TokenResponseSchema:
        email = data.email.lower()
        if await self.db.users.get_by_email(email):
            raise AlreadyExistsError("User with this email already exists")
        hashed = self.hasher.hash(data.password)
        user = await self.db.users.create(
            UserInternalCreateSchema(email=email, password=hashed)
        )
        return self._issue_tokens(user)

    async def login(self, credentials: LoginSchema) -> TokenResponseSchema:
        email = credentials.email.lower()
        internal = await self.db.users.get_internal_by_email(email)
        if internal is None:
            raise InvalidCredentialsError()
        if not self.hasher.verify(credentials.password, internal.password):
            raise InvalidCredentialsError()
        return self._issue_tokens(internal)

    async def refresh(self, refresh_token: str) -> TokenResponseSchema:
        payload = self.jwt.decode(refresh_token)  # raises UnauthorizedError on bad token
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedError("Invalid token payload")
        try:
            user = await self.db.users.get_one(UUID(sub))
        except EntityNotFoundError as exc:
            raise UnauthorizedError("User no longer exists") from exc
        return self._issue_tokens(user)

    def _issue_tokens(self, user: UserReadSchema) -> TokenResponseSchema:
        base = {"sub": str(user.id), "email": user.email}
        access = self.jwt.encode({**base, "type": "access"})
        refresh_minutes = settings.jwt.refresh_token_expire_days * 24 * 60
        refresh = self.jwt.encode(
            {**base, "type": "refresh"},
            expires_delta_minutes=refresh_minutes,
        )
        return TokenResponseSchema(access_token=access, refresh_token=refresh)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest src/tests/services/test_auth_service_tokens.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/auth.py src/tests/services/
git commit -m "feat(services): add AuthService with register/login/refresh"
```

---

## Task 16: Add `api/v1/users.py`

**Files:**
- Create: `src/api/v1/users.py`

- [ ] **Step 1: Create the file**

```python
from uuid import UUID

from fastapi import APIRouter, status
from fastapi_pagination import Page

from src.api.dependencies.auth import CurrentUserDep
from src.api.dependencies.db import DbTransactionDep
from src.schemas.users import (
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from src.services.users import UsersService

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("", response_model=Page[UserReadSchema])
async def list_users(db: DbTransactionDep, _: CurrentUserDep) -> Page[UserReadSchema]:
    return await UsersService(db).list()


@users_router.get("/{user_id}", response_model=UserReadSchema)
async def get_user(user_id: UUID, db: DbTransactionDep, _: CurrentUserDep) -> UserReadSchema:
    return await UsersService(db).get(user_id)


@users_router.post("", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateSchema, db: DbTransactionDep, _: CurrentUserDep
) -> UserReadSchema:
    return await UsersService(db).create(data)


@users_router.patch("/{user_id}", response_model=UserReadSchema)
async def update_user(
    user_id: UUID,
    data: UserUpdateSchema,
    db: DbTransactionDep,
    _: CurrentUserDep,
) -> UserReadSchema:
    return await UsersService(db).update(user_id, data)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID, db: DbTransactionDep, _: CurrentUserDep
) -> None:
    await UsersService(db).delete(user_id)
```

- [ ] **Step 2: Commit**

```bash
git add src/api/v1/users.py
git commit -m "feat(api): add users router"
```

---

## Task 17: Add `api/v1/auth.py`

**Files:**
- Create: `src/api/v1/auth.py`

- [ ] **Step 1: Create the file**

```python
from fastapi import APIRouter, status

from src.api.dependencies.auth import CurrentUserDep
from src.api.dependencies.db import DbTransactionDep
from src.schemas.auth import (
    LoginSchema,
    RefreshTokenSchema,
    TokenResponseSchema,
)
from src.schemas.users import UserCreateSchema
from src.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=TokenResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register(data: UserCreateSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).register(data)


@auth_router.post("/login", response_model=TokenResponseSchema)
async def login(credentials: LoginSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).login(credentials)


@auth_router.post("/refresh", response_model=TokenResponseSchema)
async def refresh(data: RefreshTokenSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).refresh(data.refresh_token)


@auth_router.get("/me")
async def me(current_user: CurrentUserDep) -> dict:
    return current_user
```

- [ ] **Step 2: Commit**

```bash
git add src/api/v1/auth.py
git commit -m "feat(api): add auth router (register, login, refresh, me)"
```

---

## Task 18: Wire routers in `api/v1/__init__.py`

**Files:**
- Modify: `src/api/v1/__init__.py`

- [ ] **Step 1: Replace the file contents**

```python
from fastapi import APIRouter

from src.api.v1.auth import auth_router
from src.api.v1.users import users_router

api_v1_router = APIRouter(prefix="/template/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
```

- [ ] **Step 2: Commit**

```bash
git add src/api/v1/__init__.py
git commit -m "feat(api): wire auth and users routers into v1"
```

---

## Task 19: (Removed — already covered by Task 4 verification + Task 8 step 2)

Boilerplate's `src/migrations/env.py` already does `from src.models import *`, and Task 8 step 2 adds `from src.models.users import Users` to `src/models/__init__.py`. Together those make alembic see the `Users` table without any further env.py edit.

Skip directly to Task 20.

---

## Task 20: Generate initial alembic migration

**Files:**
- Create: `src/migrations/versions/<auto>_initial_users.py`

- [ ] **Step 1: Bring up postgres for autogenerate**

```bash
cd infra
docker compose up -d postgres
cd ..
```

(If `infra/docker-compose.yaml` defines a different service name, use that. Inspect with `docker compose config` if unsure.)

- [ ] **Step 2: Confirm `.env` points at the local DB**

Copy `infra/.env.example` to `infra/.env` if not present. Ensure `POSTGRES_*` vars match what docker-compose provisions.

- [ ] **Step 3: Run autogenerate**

```bash
uv run alembic revision --autogenerate -m "initial users"
```

Expected: a new file `src/migrations/versions/<hash>_initial_users.py` is created describing `op.create_table("users", ...)` with the email check + unique-lower index.

- [ ] **Step 4: Inspect the generated file**

Open the generated migration. Verify:
- `op.create_table("users", ...)` includes `id UUID PK`, `email`, `password`, `created_at`, `updated_at`, `deleted_at`
- `op.create_check_constraint("ck_user_email_lowercase", ...)` is present
- `op.create_index("uq_user_email_lower", ...)` is unique and uses `lower(email)`

If any are missing, edit the migration file by hand to match the model.

- [ ] **Step 5: Apply the migration**

```bash
uv run alembic upgrade head
```

Expected: success. Verify with:

```bash
docker compose -f infra/docker-compose.yaml exec postgres psql -U postgres -d postgres -c "\dt"
```

(Adjust user/db to match your env.) Expected: `users` table listed.

- [ ] **Step 6: Commit**

```bash
git add src/migrations/versions/
git commit -m "feat(migrations): initial users migration"
```

---

## Task 21: Add `RequestIDMiddleware`

**Files:**
- Create: `src/api/middlewares/__init__.py`
- Create: `src/api/middlewares/request_id.py`

- [ ] **Step 1: Create empty package marker**

```bash
mkdir -p src/api/middlewares
touch src/api/middlewares/__init__.py
```

- [ ] **Step 2: Create the middleware**

`src/api/middlewares/request_id.py`:

```python
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a request ID (echo `X-Request-ID` if provided, else generate)."""

    HEADER = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(self.HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self.HEADER] = request_id
        return response
```

- [ ] **Step 3: Commit**

```bash
git add src/api/middlewares/__init__.py src/api/middlewares/request_id.py
git commit -m "feat(middlewares): add RequestIDMiddleware"
```

---

## Task 22: Add `ErrorHandlerMiddleware`

**Files:**
- Create: `src/api/middlewares/error_handler.py`

- [ ] **Step 1: Create the file**

```python
import traceback
from typing import Callable

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.observability.logging import get_logger
from src.exceptions.services.base import BaseServiceException

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch uncaught exceptions and return a structured 500.

    `BaseServiceException` is intentionally NOT caught here — those are handled
    by `register_exception_handlers`. This middleware is the final safety net.
    """

    def __init__(self, app, debug: bool = False) -> None:
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except BaseServiceException:
            raise  # let FastAPI's exception handlers run
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "Unhandled exception | type=%s message=%s path=%s method=%s request_id=%s",
                exc.__class__.__name__,
                str(exc),
                request.url.path,
                request.method,
                request_id,
                exc_info=True,
            )
            payload: dict = {
                "detail": "Internal server error",
                "type": "InternalServerError",
                "request_id": request_id,
            }
            if self.debug:
                payload["debug"] = {
                    "exception": exc.__class__.__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc().splitlines(),
                }
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=payload,
            )
```

- [ ] **Step 2: Commit**

```bash
git add src/api/middlewares/error_handler.py
git commit -m "feat(middlewares): add ErrorHandlerMiddleware"
```

---

## Task 23: Add `SecurityHeadersMiddleware`

**Files:**
- Create: `src/api/middlewares/security_headers.py`

- [ ] **Step 1: Create the file**

```python
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject baseline security headers and strip server-identifying ones."""

    DOCS_PATHS = ("/template/docs", "/template/redoc", "/template/openapi.json")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        path = request.url.path

        response.headers.pop("X-Powered-By", None)
        response.headers.pop("Server", None)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )

        if any(path.startswith(p) for p in self.DOCS_PATHS):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        else:
            response.headers.setdefault(
                "Content-Security-Policy", "default-src 'self'; frame-ancestors 'none';"
            )
        return response
```

- [ ] **Step 2: Commit**

```bash
git add src/api/middlewares/security_headers.py
git commit -m "feat(middlewares): add SecurityHeadersMiddleware"
```

---

## Task 24: Add `TimingMiddleware`

**Files:**
- Create: `src/api/middlewares/timing.py`

- [ ] **Step 1: Create the file**

```python
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.observability.logging import get_logger

logger = get_logger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """Add `X-Process-Time` header and log slow requests."""

    HEADER = "X-Process-Time"

    def __init__(
        self,
        app,
        slow_threshold_ms: float = 1000.0,
        log_slow_requests: bool = True,
    ) -> None:
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        self.log_slow_requests = log_slow_requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        response.headers[self.HEADER] = f"{elapsed_ms:.2f}ms"
        request.state.process_time_ms = elapsed_ms

        if self.log_slow_requests and elapsed_ms > self.slow_threshold_ms:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                "Slow request | method=%s path=%s duration_ms=%.2f request_id=%s",
                request.method,
                request.url.path,
                elapsed_ms,
                request_id,
            )
        return response
```

- [ ] **Step 2: Commit**

```bash
git add src/api/middlewares/timing.py
git commit -m "feat(middlewares): add TimingMiddleware"
```

---

## Task 25: Wire middlewares + add settings flag

**Files:**
- Modify: `src/core/settings.py`
- Modify: `src/main.py`

- [ ] **Step 1: Add `slow_request_threshold_ms` to settings**

Open `src/core/settings.py`. Add inside the `Settings` class (near `cors_allow_origins`):

```python
    slow_request_threshold_ms: float = 1000.0
```

- [ ] **Step 2: Wire middlewares in `main.py`**

In `src/main.py`, locate the existing `app.add_middleware(CORSMiddleware, ...)` call. Replace the surrounding middleware section with:

```python
    from src.api.middlewares.error_handler import ErrorHandlerMiddleware
    from src.api.middlewares.request_id import RequestIDMiddleware
    from src.api.middlewares.security_headers import SecurityHeadersMiddleware
    from src.api.middlewares.timing import TimingMiddleware

    app.add_middleware(
        ErrorHandlerMiddleware, debug=settings.app_env == "development"
    )
    app.add_middleware(
        TimingMiddleware,
        slow_threshold_ms=settings.slow_request_threshold_ms,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

(Order matters: `add_middleware` is LIFO — the LAST added runs FIRST on inbound. We want `RequestIDMiddleware` to run first inbound so all downstream middlewares see the request_id. `ErrorHandlerMiddleware` is added FIRST so it's outermost on outbound — it catches anything the others raise.)

- [ ] **Step 3: Commit**

```bash
git add src/core/settings.py src/main.py
git commit -m "feat(main): wire custom middlewares (request_id, timing, security_headers, error_handler)"
```

---

## Task 26: Add `/template/ready` endpoint

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Add the readiness handler**

In `src/main.py`, just below the existing `health()` handler, add:

```python
    @app.get("/template/ready", include_in_schema=False)
    async def ready() -> dict:
        from sqlalchemy import text

        from src.db.postgres.instance import AsyncSessionFactory

        try:
            async with AsyncSessionFactory() as s:
                await s.execute(text("SELECT 1"))
            db_state = "ok"
        except Exception:
            db_state = "failed"
        is_ready = db_state == "ok"
        return {
            "status": "ready" if is_ready else "degraded",
            "checks": {"database": db_state},
        }
```

(If you want a 503 on degradation, return a `JSONResponse` with status 503 — kept simple here for the template.)

- [ ] **Step 2: Commit**

```bash
git add src/main.py
git commit -m "feat(main): add /template/ready readiness probe"
```

---

## Task 27: Refresh `.github/workflows/ci.yml` for uv toolchain

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Replace the file**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Ruff
        run: uv run ruff check src/

      - name: Pytest
        env:
          DB_HOST: localhost
          DB_PORT: 5432
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_DATABASE: postgres
          JWT_SECRET_KEY: ci-test-secret
        run: uv run pytest src/tests/ -v
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: replace workflow with uv + ruff + pytest pipeline"
```

---

## Task 28: Refresh `.gitignore`

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Append cache patterns**

Append (or ensure present) the following lines in `.gitignore`:

```
# OS
.DS_Store

# Caches
.pytest_cache/
.ruff_cache/
.mypy_cache/
__pycache__/

# Virtualenv
.venv/

# Env files (keep .env.example committed)
infra/.env
.env
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: extend .gitignore for caches, venv, env files"
```

---

## Task 29: Rewrite `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace with a template-oriented README**

```markdown
# fastapi-microservice

A production-ready FastAPI template with postgres, JWT auth, structured exceptions, and a worked auth/users example.

## Stack

- FastAPI 0.115 / Starlette
- SQLAlchemy 2.0 (async) + asyncpg + Alembic
- Pydantic 2 / pydantic-settings
- PyJWT + passlib[bcrypt]
- fastapi-pagination, prometheus-fastapi-instrumentator, sentry-sdk
- APScheduler (lifespan-driven)
- uv + ruff + pre-commit

## Layout

```
src/
├── api/                     # routers, dependencies, custom middlewares, exception handlers
├── core/                    # settings, JWT config, postgres config, logging, timezone
├── db/                      # async engine, session factory, mixins, declarative base
├── enums/
├── exceptions/
│   ├── repositories/
│   └── services/            # raised by services; auto-translated to JSON 4xx/5xx
├── integrations/
├── jobs/lifespan.py         # APScheduler entry; register cron jobs here
├── managers/db/             # TransactionManager / ReadonlyManager — wire repos here
├── mappers/                 # ORM ↔ Pydantic translation
├── migrations/              # Alembic
├── models/                  # SQLAlchemy ORM models
├── repositories/            # CRUD on models, returns mapped entities
├── schemas/                 # Pydantic request/response schemas
├── security/                # JWT + bcrypt (interfaces + implementations)
├── services/                # business logic (BaseService[TM])
└── tests/
```

## Quickstart

```bash
git clone <fork>
cd fastapi-microservice

cp infra/.env.example infra/.env
# edit infra/.env with your local POSTGRES_* and JWT_SECRET_KEY

# bring up postgres
docker compose -f infra/docker-compose.yaml up -d postgres

uv sync --all-extras
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

Open `http://localhost:8000/template/docs` (basic auth: `admin` / `admin` — see `Settings.docs_password`).

## Endpoints

- `POST /template/api/v1/auth/register` — create a user, returns access + refresh tokens
- `POST /template/api/v1/auth/login` — exchange credentials for tokens
- `POST /template/api/v1/auth/refresh` — exchange a refresh token for a new pair
- `GET  /template/api/v1/auth/me` — JWT payload of the current user
- `GET  /template/api/v1/users` — paginated list (auth required)
- `GET  /template/api/v1/users/{id}`
- `POST /template/api/v1/users`
- `PATCH /template/api/v1/users/{id}`
- `DELETE /template/api/v1/users/{id}`
- `GET  /template/health`
- `GET  /template/ready`
- `GET  /template/metrics` (Prometheus)

## Customizing for a new service

1. Find/replace `/template/` with `/<your-service>/` across `src/main.py` and `src/api/v1/__init__.py`.
2. Rename in `pyproject.toml`: `[project] name`, `[tool.hatch.build.targets.wheel] packages` (already `["src"]`).
3. Add domain models, schemas, mappers, repositories, services, routers — follow the `users` example.
4. Wire new repositories in `src/managers/db/transaction.py` and `readonly.py`.
5. Register your routers in `src/api/v1/__init__.py`.

## Running tests

```bash
uv run pytest src/tests/ -v
```

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for the migrated template"
```

---

## Task 30: End-to-end smoke test

**Files:**
- Test (manual / scripted): docker-compose round-trip

- [ ] **Step 1: Bring up the full stack**

```bash
cd infra
cp .env.example .env  # if not already done; edit JWT_SECRET_KEY
docker compose up -d
cd ..
```

- [ ] **Step 2: Apply migrations**

```bash
uv run alembic upgrade head
```

Expected: success.

- [ ] **Step 3: Start the API**

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

(Run in a separate shell. Or `make up` if Makefile target exists.)

- [ ] **Step 4: Hit health**

```bash
curl -sS http://localhost:8000/template/health | jq
```

Expected: `{"status": "ok", "service": "...", "version": "..."}`.

- [ ] **Step 5: Hit ready**

```bash
curl -sS http://localhost:8000/template/ready | jq
```

Expected: `{"status": "ready", "checks": {"database": "ok"}}`.

- [ ] **Step 6: Register**

```bash
curl -sS -X POST http://localhost:8000/template/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"hunter2-secure"}' | jq
```

Expected: `{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}`. Save the access token.

- [ ] **Step 7: Login with the same creds**

```bash
curl -sS -X POST http://localhost:8000/template/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"hunter2-secure"}' | jq
```

Expected: another token pair.

- [ ] **Step 8: /me with the access token**

```bash
ACCESS=...  # paste the access_token
curl -sS http://localhost:8000/template/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS" | jq
```

Expected: `{"sub": "<uuid>", "email": "alice@example.com", "type": "access", "exp": ...}`.

- [ ] **Step 9: List users (paginated)**

```bash
curl -sS "http://localhost:8000/template/api/v1/users?page=1&size=10" \
  -H "Authorization: Bearer $ACCESS" | jq
```

Expected: `{"items": [{"id": "...", "email": "alice@example.com", ...}], "total": 1, "page": 1, "size": 10, "pages": 1}`.

- [ ] **Step 10: Refresh**

```bash
REFRESH=...  # paste refresh_token from step 6
curl -sS -X POST http://localhost:8000/template/api/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}" | jq
```

Expected: a new token pair.

- [ ] **Step 11: Run pytest**

```bash
uv run pytest src/tests/ -v
```

Expected: all green.

- [ ] **Step 12: Verify Request-ID round-trip**

```bash
curl -sS -i http://localhost:8000/template/health -H 'X-Request-ID: smoke-123' | grep -i 'x-request-id'
```

Expected: `x-request-id: smoke-123` in response headers.

- [ ] **Step 13: Stop services**

```bash
cd infra && docker compose down && cd ..
```

- [ ] **Step 14: Open a PR**

```bash
git push -u origin boilerplate-migration
gh pr create --title "Migrate to boilerplate skeleton (greenfield port)" \
  --body "Replaces the old kitchen-sink template with the new minimal-but-complete boilerplate. See docs/superpowers/specs/2026-05-05-fastapi-microservice-migration-design.md and docs/superpowers/plans/2026-05-05-fastapi-microservice-migration.md."
```

---

## Done

The repo is now:
- Built on the new boilerplate foundation
- Ships a working auth/users example
- Has request_id, timing, security_headers, error_handler middlewares wired
- CI runs ruff + pytest against a real Postgres
- README documents the template-fork workflow

Old code remains accessible at the `pre-migration` tag and `pre-migration-backup` branch.
