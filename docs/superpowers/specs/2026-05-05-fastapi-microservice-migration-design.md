# fastapi-microservice — Migration Design (Boilerplate Port)

**Date:** 2026-05-05
**Status:** Draft — pending user review
**Target repo:** `github/microservices/fastapi-microservice` (in-place; existing git history preserved)
**Source pattern:** `safia/safia-shared/boilerplate/template_service`

---

## 1. Goal

Replace the contents of the existing `fastapi-microservice` GitHub template with a fresh service skeleton derived from the new `boilerplate/template_service` design, plus a worked auth/users example. The result remains a GitHub template that other developers fork and customize.

The old service was a personal "kitchen-sink" template that accumulated every feature its author touched (mongo, mysql, redis, websockets, rate limiting, resilience, throttle, custom metrics middleware, OpenTelemetry/Jaeger). The new style is intentionally minimal, postgres-only, and has cleaner conventions for repositories, services, managers, and exception handling.

## 2. Scope: "Standard"

### Included (foundation — copied from boilerplate as-is)

- Postgres + asyncpg + SQLAlchemy 2.0 async
- Alembic migrations
- Generic `BaseRepository[TModel, TEntity]` with CRUD + soft-delete filter
- Generic `BaseService[TM]` with `paginated_list` helper
- `TransactionManager` / `ReadonlyManager` pattern for unit-of-work
- `BaseDataMapper` for ORM ↔ Pydantic translation
- `BaseModel` mixin (UUID PK + timestamps + soft-delete)
- JWT encode/decode (`PyJWTHandler`) with HS algorithms
- `register_exception_handlers` — service exceptions auto-map to JSON responses
- `PermissionChecker` dependency factory
- APScheduler-backed lifespan (`combined_lifespan`)
- Sentry integration (opt-in via `SENTRY_DSN`)
- Prometheus metrics via `prometheus_fastapi_instrumentator`
- `fastapi-pagination` for paginated responses
- HTTP Basic auth-protected `/docs` + `/openapi.json`
- Tashkent timezone helper (`src/core/timezone.py`)
- pre-commit, ruff, uv, hatchling — full toolchain

### Included (worked example — ported from old, in new style)

- `auth` endpoints: `POST /register`, `POST /login`, `POST /refresh`, `GET /me`
- `users` endpoints: `GET /`, `GET /{id}`, `POST /`, `PATCH /{id}`, `DELETE /{id}`
- `Users` model (UUID PK, lowercased-email unique constraint via index + `before_insert/update` listener)
- `BcryptPasswordHasher` (passlib) — added to boilerplate's `security/` layer
- Initial alembic migration for the `users` table
- Four extra middlewares ported into `src/api/middlewares/`:
  - `RequestIDMiddleware` (sets `request.state.request_id`, echoes `X-Request-ID`)
  - `ErrorHandlerMiddleware` (catches uncaught exceptions, structured 500 response, debug traceback when `app_env=development`)
  - `SecurityHeadersMiddleware` (HSTS, X-Frame-Options, CSP for docs paths)
  - `TimingMiddleware` (X-Process-Time header + slow-request log)

### Dropped

| Old item | Reason |
|---|---|
| `mongo`, `mysql`, `redis` (db/, core/, repositories/) | Not in Standard scope; postgres-only template |
| `websockets`, `managers/websocket.py`, `api/ws.py` | Out of scope |
| `core/rate_limit.py`, `core/throttle/`, `core/resilience/` (circuit_breaker, retry) | Out of scope; Redis-dependent |
| `core/http_client.py` | Use `httpx` directly per integration |
| `core/observability/metrics.py`, `middlewares/metrics.py` | Replaced by `prometheus_fastapi_instrumentator` |
| `core/pagination.py`, `schemas/pagination.py`, `api/dependencies/pagination.py` | Replaced by `fastapi-pagination` |
| `infra/nginx.conf` | Out of scope |
| OpenTelemetry / Jaeger setup in `main.py` | Replaced by Sentry tracing |
| `cli/admin.py` (referenced in old pyproject `[project.scripts]`, file may not exist) | Out of scope |
| `.pytest_cache/`, `.ruff_cache/`, `.DS_Store` (currently committed) | Add to `.gitignore` |
| `poetry.lock` | Replaced by `uv.lock` |
| `pytest.ini` | Replaced by `[tool.pytest.ini_options]` in `pyproject.toml` |
| Failed-login lockout, refresh token revocation (Redis-backed) | Dropped from auth example. Rationale: requires Redis, which is out of scope. Re-add with the `redis` extension when needed. |

### Decisions made (no further user input)

- **PK type:** UUID (boilerplate convention; old service used integer)
- **URL prefix:** keep `/template/...` namespacing as in boilerplate (user confirmed). Other devs forking the template will rename to their service prefix
- **Auth scope:** minimal viable (register/login/refresh/me) without Redis-dependent hardening
- **Refresh token expiry:** boilerplate already exposes `refresh_token_expire_days: int = 7`. Auth service converts to minutes when calling `jwt.encode(expires_delta_minutes=...)`.
- **Error response shape:** boilerplate's `{"detail": message, "type": ClassName}` is kept for service-exception responses. The middleware-level `ErrorHandlerMiddleware` only handles **uncaught** exceptions (final safety net), not the `BaseServiceException` family
- **Soft-delete:** users use the soft-delete column (compatible with `BaseRepository._active_filter`)

## 3. Final Structure

```
fastapi-microservice/
├── .github/workflows/ci.yml      # refreshed: ruff + pytest + uv toolchain
├── .pre-commit-config.yaml       # from boilerplate
├── .python-version               # 3.12
├── .gitignore                    # boilerplate + .DS_Store, .pytest_cache, .ruff_cache
├── alembic.ini                   # boilerplate
├── Makefile                      # boilerplate
├── pyproject.toml                # boilerplate deps + passlib[bcrypt]
├── ruff.toml                     # boilerplate
├── README.md                     # rewritten for template usage
├── uv.lock                       # regenerated
├── docs/superpowers/specs/...    # this design doc + future plans
├── infra/
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── docker-compose.prod.yaml
│   └── commands/{api.sh, entrypoint.sh}
└── src/
    ├── __init__.py
    ├── main.py                   # boilerplate + 4 custom middlewares wired
    ├── api/
    │   ├── __init__.py
    │   ├── dependencies/{auth.py, db.py, docs.py, permission.py}
    │   ├── handlers/exceptions.py
    │   ├── middlewares/          # NEW (extends boilerplate)
    │   │   ├── __init__.py
    │   │   ├── request_id.py
    │   │   ├── error_handler.py
    │   │   ├── security_headers.py
    │   │   └── timing.py
    │   └── v1/
    │       ├── __init__.py       # api_v1_router with auth + users sub-routers
    │       ├── auth.py
    │       └── users.py
    ├── core/
    │   ├── config.py             # (existing in boilerplate, currently empty)
    │   ├── jwt.py                # JWTSettings (boilerplate provides refresh_token_expire_days)
    │   ├── postgres.py           # PostgresSettings
    │   ├── settings.py           # central Settings
    │   ├── timezone.py
    │   └── observability/logging.py
    ├── db/
    │   ├── factory.py
    │   ├── postgres/{instance.py, mixins/{pk,timestamp,softdeletion}.py}
    │   └── sqlalchemy/base.py
    ├── enums/api/permissions.py
    ├── exceptions/
    │   ├── repositories/
    │   │   ├── base.py           # boilerplate
    │   │   └── users.py          # NEW — repo-layer user exceptions
    │   └── services/
    │       ├── base.py           # boilerplate
    │       └── auth.py           # NEW — service-layer auth exceptions
    ├── integrations/base.py
    ├── jobs/lifespan.py
    ├── managers/db/{base.py, transaction.py, readonly.py}
    │                              # transaction.py wires UsersRepository
    ├── mappers/
    │   ├── base.py
    │   └── users.py              # NEW
    ├── migrations/
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       └── <hash>_initial_users.py   # NEW
    ├── models/
    │   ├── base.py               # boilerplate (UUID + ts + soft-delete)
    │   └── users.py              # NEW
    ├── repositories/
    │   ├── base.py               # boilerplate
    │   └── users.py              # NEW
    ├── schemas/
    │   ├── auth.py               # NEW
    │   └── users.py              # NEW
    ├── security/
    │   ├── interfaces/
    │   │   ├── jwt.py            # boilerplate
    │   │   └── hasher.py         # NEW
    │   └── implementations/
    │       ├── jwt.py            # boilerplate
    │       └── bcrypt.py         # NEW
    └── services/
        ├── base.py               # boilerplate
        ├── auth.py               # NEW
        └── users.py              # NEW
```

## 4. Module Designs

### 4.1 `models/users.py`

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

### 4.2 `mappers/users.py`

```python
from src.mappers.base import BaseDataMapper
from src.models.users import Users
from src.schemas.users import UserReadSchema


class UsersMapper(BaseDataMapper[Users, UserReadSchema]):
    model = Users
    schema = UserReadSchema
```

### 4.3 `repositories/users.py`

```python
from sqlalchemy import select

from src.mappers.users import UsersMapper
from src.models.users import Users
from src.repositories.base import BaseRepository
from src.schemas.users import UserReadSchema


class UsersRepository(BaseRepository[Users, UserReadSchema]):
    model = Users
    mapper = UsersMapper
    entity_name = "User"

    async def get_by_email(self, email: str) -> UserReadSchema | None:
        stmt = self._active_filter(select(Users).where(Users.email == email))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        return self.mapper.map_to_domain_entity(instance) if instance else None

    async def get_internal_by_email(self, email: str) -> "UserInternalSchema | None":
        # Returns the internal schema (includes hashed password). Service-only.
        from src.schemas.users import UserInternalSchema

        stmt = self._active_filter(select(Users).where(Users.email == email))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        return UserInternalSchema.model_validate(instance, from_attributes=True) if instance else None
```

### 4.4 `managers/db/transaction.py` (wiring)

```python
from src.managers.db.base import BaseTransactionManager
from src.repositories.users import UsersRepository


class TransactionManager(BaseTransactionManager):
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

`ReadonlyManager` mirrors with the same wiring (no commits).

### 4.5 `schemas/users.py`

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.base import UUIDSchema, TimestampSchema  # NEW small module — see 4.10


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

### 4.6 `schemas/auth.py`

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

### 4.7 `security/interfaces/hasher.py`, `security/implementations/bcrypt.py`

```python
# interfaces/hasher.py
from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...


# implementations/bcrypt.py
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

### 4.8 `services/auth.py`

```python
from uuid import UUID

from src.exceptions.repositories.base import EntityNotFoundError
from src.exceptions.services.auth import InvalidCredentialsError
from src.exceptions.services.base import (
    AlreadyExistsError,
    UnauthorizedError,
)
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
from src.core.settings import settings


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
        payload = self.jwt.decode(refresh_token)  # raises UnauthorizedError
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        try:
            user = await self.db.users.get_one(UUID(payload["sub"]))
        except EntityNotFoundError as exc:
            raise UnauthorizedError("User no longer exists") from exc
        return self._issue_tokens(user)

    def _issue_tokens(self, user: UserReadSchema) -> TokenResponseSchema:
        base = {"sub": str(user.id), "email": user.email}
        access = self.jwt.encode({**base, "type": "access"})
        refresh = self.jwt.encode(
            {**base, "type": "refresh"},
            expires_delta_minutes=settings.jwt.refresh_token_expire_days * 24 * 60,
        )
        return TokenResponseSchema(access_token=access, refresh_token=refresh)
```

**4.8.1 — Password access for login.** The repo's `get_by_email` returns the public `UserReadSchema`, which **excludes** `password`. The auth service needs the hash for verification. The chosen approach (shown in 4.3): add `get_internal_by_email(email) -> UserInternalSchema | None` that maps via the service-only `UserInternalSchema`. The internal schema is never returned from a router.

### 4.9 `services/users.py`, `api/v1/users.py`, `api/v1/auth.py`

Standard CRUD + auth flows. Routers are thin — no `try/except`; `register_exception_handlers` translates `BaseServiceException` subclasses into JSON responses. See 4.11 for exception classes.

### 4.10 `schemas/base.py` (small new module)

Boilerplate doesn't ship base schemas. Add a thin file with shared mixins:

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

### 4.11 Exceptions

Add the following on top of boilerplate's `exceptions/services/base.py` and `exceptions/repositories/base.py`:

```python
# exceptions/services/auth.py
from http import HTTPStatus

from src.exceptions.services.base import BaseServiceException


class InvalidCredentialsError(BaseServiceException):
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


# exceptions/repositories/users.py — empty module, reserved for future user-specific repo errors
```

### 4.12 Middlewares

`src/api/middlewares/` — ported from old service, simplified:

- **request_id.py** — generate or echo `X-Request-ID`, store on `request.state.request_id`
- **error_handler.py** — catch any uncaught `Exception` (ie. NOT `BaseServiceException`, which is handled by `register_exception_handlers`); log with traceback; return 500 with `{"detail", "type", "request_id"}`
- **security_headers.py** — inject HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy; CSP for `/template/docs` paths
- **timing.py** — measure latency, set `X-Process-Time`, log requests over a configurable threshold

Wired in `src/main.py`:

```python
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(ErrorHandlerMiddleware, debug=settings.app_env == "development")
app.add_middleware(CORSMiddleware, ...)  # already in boilerplate
```

(Order: outermost-last for `add_middleware`; `ErrorHandlerMiddleware` should run as early as possible to catch errors from inner middlewares too.)

### 4.13 Settings additions

`src/core/jwt.py` is unchanged from boilerplate — it already provides `refresh_token_expire_days: int = 7`.
`src/core/settings.py` adds `slow_request_threshold_ms: float = 1000.0` for `TimingMiddleware`.

### 4.14 Pagination

Use `fastapi-pagination`'s `Page[UserReadSchema]` directly in `users` list endpoint via `BaseService.paginated_list`. No custom pagination schemas.

### 4.15 Health endpoint

Boilerplate already has `/template/health` returning `{status, service, version}`. Add a `/template/ready` that runs `SELECT 1` against the DB. No `/live` (k8s `tcpSocket` probe is enough).

### 4.16 Initial migration

`alembic revision --autogenerate -m "initial users"` after wiring `Users` into `target_metadata` in `src/migrations/env.py`. Ship the generated file under `src/migrations/versions/`.

## 5. `pyproject.toml` Diff vs Boilerplate

Add to `[project] dependencies`:
- `passlib[bcrypt]>=1.7.4` (already in boilerplate — confirm)
- `email-validator>=2.0` (transitive of `pydantic[email]` — required for `EmailStr`)

Add to `[dependency-groups] dev`:
- `httpx` (for test client) — already a runtime dep
- `pytest-cov>=5.0` (optional but useful for a template)

Update `[project] name` to `fastapi-microservice` and `[tool.hatch.build.targets.wheel] packages = ["src"]`.

## 6. Build Sequence

The migration is staged so each commit leaves a working tree:

1. **Backup branch** — `git checkout -b pre-migration-backup` and push, then return to `main`. (Old code recoverable forever.)
2. **Wipe target tree** — remove old `src/`, `infra/`, `docs/openapi.json`, `docs/collection.json`, `poetry.lock`, `pytest.ini`, `.pytest_cache/`, `.ruff_cache/`. Keep `.git/`, `.github/`, `docs/superpowers/` (this spec lives there), `README.md` (rewritten next).
3. **Copy boilerplate skeleton** — `cp -r boilerplate/template_service/. fastapi-microservice/` (excluding `.gitea/`).
4. **Add user-domain modules** — models, schemas, mappers, repositories, services, exceptions, routers in dependency order:
   1. `models/users.py`
   2. `schemas/{base,users,auth}.py`
   3. `mappers/users.py`
   4. `exceptions/services/auth.py`
   5. `repositories/users.py` (with `get_by_email` and `get_internal_by_email`)
   6. `managers/db/{transaction,readonly}.py` — wire repositories
   7. `security/{interfaces/hasher,implementations/bcrypt}.py`
   8. `services/{users,auth}.py`
   9. `api/v1/{users,auth}.py`
   10. `api/v1/__init__.py` — include sub-routers
5. **Add middlewares** — `src/api/middlewares/{request_id,error_handler,security_headers,timing}.py`. Wire in `main.py`.
6. **Initial alembic migration** — autogenerate + commit.
7. **Refresh `.github/workflows/ci.yml`** — uv setup, ruff check, pytest.
8. **Refresh `README.md`** — quickstart for forks, env vars, run/migrate commands.
9. **`.gitignore` additions** — `.DS_Store`, `.pytest_cache/`, `.ruff_cache/`, `.venv/`.
10. **Smoke test** — `make up`, hit `/template/health`, register/login/me cycle, run pytest skeleton.

## 7. Testing Strategy

- `src/tests/` (boilerplate `pyproject` already points pytest at this path)
- `pytest-asyncio` in auto mode
- Smoke tests:
  - `test_health.py` — health + ready
  - `test_auth_flow.py` — register → login → /me round-trip with a real Postgres (docker-compose)
- Unit tests deferred to template users; the template ships smoke coverage only.

## 8. Risks & Open Questions

| Risk | Mitigation |
|---|---|
| Other devs may have forks/clones of the old structure; massive structural change will diverge them | Acceptable — templates are starting points, not living libraries. Tag `v0.x` on the pre-migration commit so forks have a stable reference. |
| `BaseRepository.create()` calls `self.mapper.map_to_persistence_entity(schema)` which constructs `Users(email=..., password=hashed)` — works only if `UserInternalCreateSchema` carries the hashed password as the `password` field | The schema is named "Internal" specifically for this; auth service builds it explicitly. |
| `BaseRepository.soft_delete` uses `datetime.utcnow()` (deprecated in 3.12) | Bug in boilerplate. Out of scope for this migration; file as a follow-up issue against the boilerplate. |
| `email-validator` may need to be made an explicit dep for `EmailStr` | Add it to `pyproject.toml` to be safe. |

## 9. Out of Scope (Future Work)

- Redis-backed rate limiting / login lockout / refresh-token revocation
- WebSockets
- Mongo / MySQL adapters
- Distributed tracing (OpenTelemetry / Jaeger)
- Permission-service integration (boilerplate ships the dependency; lookup is left as TODO)
- CLI admin commands (`fastapi-microservice-admin`) — referenced in old pyproject but file doesn't appear in tree

## 10. Acceptance Criteria

- `docker compose up` starts the service against a local Postgres
- `POST /template/api/v1/auth/register` creates a user and returns tokens
- `POST /template/api/v1/auth/login` with the same credentials returns tokens
- `GET /template/api/v1/auth/me` with the access token returns the user
- `GET /template/health` returns `{"status": "ok"}`
- `make migrate` applies the initial users migration cleanly on an empty DB
- Ruff and pytest pass in CI
