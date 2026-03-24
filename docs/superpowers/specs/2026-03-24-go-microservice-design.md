# Go Microservice Template — Design Spec

## Overview

A production-grade Go microservice template built with Fiber, mirroring the architecture and features of the existing FastAPI microservice. Idiomatic Go structure with clean architecture principles.

**Tech stack:** Go, Fiber, GORM, golang-migrate, zerolog, go-redis, golang-jwt, bcrypt, Viper

**Module:** `github.com/the_elita/go-microservice`
**Directory:** `Desktop/apps/github/go-microservice`

---

## Project Structure

```
go-microservice/
├── cmd/
│   └── server/
│       └── main.go                 # Entry point, wires everything, graceful shutdown
├── internal/
│   ├── api/
│   │   ├── router.go               # Root router, mounts all groups
│   │   ├── handlers/
│   │   │   ├── auth.go             # Register, login, refresh, me
│   │   │   ├── users.go            # CRUD + pagination
│   │   │   └── health.go           # /health, /live, /ready, GET /
│   │   └── middleware/
│   │       ├── cors.go
│   │       ├── error_handler.go
│   │       ├── rate_limiter.go
│   │       ├── request_id.go
│   │       ├── security_headers.go
│   │       ├── timing.go
│   │       └── trusted_host.go
│   ├── config/
│   │   └── config.go               # Env-based config (Viper)
│   ├── db/
│   │   ├── factory.go              # Provider factory (postgres/mysql/mongo)
│   │   ├── postgres.go
│   │   ├── mysql.go
│   │   ├── mongo.go
│   │   ├── redis.go
│   │   ├── migrate.go              # Embed + run migrations
│   │   └── migrations/
│   │       ├── 000001_init.up.sql
│   │       └── 000001_init.down.sql
│   ├── domain/
│   │   ├── models/
│   │   │   └── user.go             # GORM model with soft delete, timestamps
│   │   ├── dto/
│   │   │   ├── auth.go             # Login/register request/response
│   │   │   ├── users.go            # User CRUD DTOs
│   │   │   └── pagination.go       # Pagination request/response
│   │   └── errors/
│   │       ├── api.go              # HTTP error types
│   │       ├── repository.go       # Data access errors
│   │       └── service.go          # Business logic errors
│   ├── repository/
│   │   ├── interfaces.go           # Repository interfaces
│   │   ├── user_postgres.go        # Postgres implementation
│   │   ├── user_mysql.go           # MySQL implementation
│   │   └── user_mongo.go           # MongoDB implementation
│   ├── service/
│   │   ├── auth.go                 # Auth logic, JWT, brute-force protection
│   │   └── users.go                # User CRUD + pagination, model↔DTO conversion
│   ├── security/
│   │   ├── interfaces.go           # Hasher and TokenService interfaces
│   │   ├── jwt.go                  # TokenService implementation
│   │   └── hasher.go               # Hasher implementation (bcrypt)
│   └── logger/
│       └── logger.go               # Structured logging (zerolog)
├── infra/
│   ├── Dockerfile
│   ├── docker-compose.local.yml
│   ├── nginx.conf
│   ├── .env-example
│   └── commands/
│       ├── entrypoint.sh
│       └── migrate.sh
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── Makefile
├── go.mod
└── go.sum
```

---

## Graceful Shutdown

`cmd/server/main.go` handles `SIGINT`/`SIGTERM` via `os.Signal` channel:

1. Call `app.Shutdown()` to stop accepting new connections
2. Close Redis client
3. Close MongoDB client (if active)
4. Close GORM DB connection pool (`sqlDB.Close()`)
5. Log shutdown complete

Startup pings Redis and DB to verify connectivity (matching FastAPI's lifespan handler).

---

## Database & Models

### User Model (GORM)

Fields: `ID`, `CreatedAt`, `UpdatedAt`, `DeletedAt` (GORM soft delete), `Email` (unique, case-insensitive, lowercase enforced), `HashedPassword`.

GORM hooks `BeforeCreate`/`BeforeUpdate` normalize email to lowercase.

### Database Factory

`NewDatabase(ctx context.Context, cfg Config)` returns `*gorm.DB` based on `DB_PROVIDER` env var:
- **Postgres**: `gorm.io/driver/postgres` with connection pooling
- **MySQL**: `gorm.io/driver/mysql` with connection pooling
- **MongoDB**: `go.mongodb.org/mongo-driver` with its own repository implementation (not GORM)

Single connection mode (no read replicas). All queries go through the same `*gorm.DB` instance.

### Redis

`go-redis/redis/v9` client. Used for rate limiting, login attempt tracking, refresh token revocation. Graceful fallback when unavailable.

### Migrations (golang-migrate)

SQL files embedded via `//go:embed` in `internal/db/migrations/`. Ships with the binary. `golang-migrate` reads from `embed.FS`.

---

## Auth & Security

### JWT (`golang-jwt/jwt/v5`)

- Access token: 15min default, refresh token: 7 days default
- Claims: `user_id`, `email`, `token_type`, `exp`, `iat`
- Validation checks token type (access vs refresh)

### Security Interfaces (`internal/security/interfaces.go`)

```go
type Hasher interface {
    Hash(password string) (string, error)
    Verify(password, hash string) (bool, error)
}

type TokenService interface {
    GenerateAccessToken(userID uint, email string) (string, error)
    GenerateRefreshToken(userID uint, email string) (string, error)
    ValidateToken(tokenString string) (*Claims, error)
}
```

### Password Hashing (`golang.org/x/crypto/bcrypt`)

Implements the `Hasher` interface. Hash on registration, verify on login.

### Login Protection

- Redis-based failed attempt tracking (per-email + per-IP)
- Configurable: `auth_max_attempts` (default 5), `auth_window_seconds` (default 300), `auth_lockout_seconds` (default 900)
- Returns 429 with `Retry-After` header when locked
- Graceful skip when Redis unavailable

### Auth Middleware

- Extracts Bearer token from Authorization header
- Validates JWT, loads user from DB
- Sets user in `c.Locals("user", user)`
- Returns 401 for invalid/expired tokens

### Auth Endpoints

- `POST /api/v1/auth/register` — Create user, return token pair
- `POST /api/v1/auth/login` — Authenticate, return token pair
- `POST /api/v1/auth/refresh` — New access token from refresh token
- `GET /api/v1/auth/me` — Current user info (protected)

---

## Repository Interface

```go
type UserRepository interface {
    GetByID(ctx context.Context, id uint) (*models.User, error)
    GetByEmail(ctx context.Context, email string) (*models.User, error)
    GetAll(ctx context.Context, limit, offset int) ([]models.User, error)
    Create(ctx context.Context, user *models.User) error
    Update(ctx context.Context, user *models.User) error
    Delete(ctx context.Context, id uint) error
    Restore(ctx context.Context, id uint) error
    Count(ctx context.Context) (int64, error)
}
```

Three implementations: `user_postgres.go`, `user_mysql.go`, `user_mongo.go`.

### Model-to-DTO Conversion

Conversion between GORM models and DTOs happens in the service layer via simple helper functions within each service file (no separate mapper package).

---

## Middleware Stack

Execution order:

1. **Request ID** — UUID generation or reads `X-Request-ID`, sets on response
2. **Timing** — Request duration, `X-Process-Time` header, logs slow requests (threshold configurable via `slow_request_threshold_ms`)
3. **Security Headers** — HSTS, X-Frame-Options, CSP, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy (`strict-origin-when-cross-origin`). Strips `Server` and `X-Powered-By` headers.
4. **Trusted Host** — Validates `Host` header against configured `trusted_hosts` whitelist. Returns 421 for untrusted hosts.
5. **CORS** — Configurable `allowed_origins`, methods, credentials
6. **Rate Limiter** — Redis-backed + in-memory fallback. Separate limits and windows: `limit_get`/`time_get` for GET, `limit_ppd`/`time_ppd` for POST/PUT/DELETE. Toggleable via `rate_limit_enabled`.
7. **Error Handler** — Fiber custom error handler, structured JSON errors

### Error Response Format

```json
{
  "error": {
    "type": "UNAUTHORIZED",
    "message": "Invalid credentials",
    "request_id": "uuid-here"
  }
}
```

Error envelope wraps all errors in an `"error"` key, matching FastAPI microservice format.

---

## User CRUD Endpoints

All user endpoints require authentication (auth middleware applied to the group).

- `GET /api/v1/users` — List users (paginated)
- `GET /api/v1/users/:id` — Get user by ID
- `POST /api/v1/users` — Create user
- `PATCH /api/v1/users/:id` — Update user (email/password)
- `DELETE /api/v1/users/:id` — Soft delete user, returns `{"status": "success", "id": <id>}`

### Root Endpoint

- `GET /` — Returns service name, version, and status (smoke test)

### Pagination

Query params: `page` (1-indexed), `per_page` (1-100).
Response includes: `total_pages`, `current_page`, `total_items`, `has_next`, `has_previous`.

---

## Config (Viper)

Reads from env vars + `.env` file. Nested config struct:
- `Server`: host, port, environment, debug, trusted_hosts, app_name, app_version, api_prefix
- `JWT`: secret_key, algorithm, access_token_expiry, refresh_token_expiry
- `Auth`: max_attempts, window_seconds, lockout_seconds
- `Postgres`: DSN, pool_size, pool_max_idle, pool_max_lifetime
- `MySQL`: DSN, pool_size, pool_max_idle, pool_max_lifetime
- `MongoDB`: URI, database
- `Redis`: host, port, password, db, timeout
- `RateLimit`: enabled, limit_get, time_get, limit_ppd, time_ppd
- `CORS`: allowed_origins
- `Pagination`: max_per_page
- `Logging`: level, slow_request_threshold_ms

Environment profiles: development, test, staging, production. Validates security defaults on startup (e.g., reject wildcard trusted_hosts in production).

---

## Logging (zerolog)

- JSON output in production, pretty console in development
- Request-scoped logging with request ID
- Log level configurable via env var
- Attached to Fiber context for per-request access

---

## Infrastructure

### Dockerfile (multi-stage)

- `builder`: Go build, compile binary
- `production`: Alpine/distroless with just the binary (~15-20MB image)

### Docker Compose

Services: API, Postgres 17, MySQL 8.4, MongoDB 7, Redis 7, Nginx.
DB profiles (only active provider starts). Health checks on all services.

### CI (GitHub Actions)

Trigger: push to main + PRs. Services: Postgres + Redis.
Steps: checkout, setup Go, lint (golangci-lint), unit tests, integration tests.

### Makefile

`run`, `build`, `test`, `test-unit`, `test-integration`, `lint`, `fmt`, `migrate-up`, `migrate-down`, `migrate-create`, `docker-up-postgres`, `docker-up-mysql`, `docker-up-mongo`.

---

## Testing

Go built-in `testing` + `testify` for assertions.

- Tests live next to the code (Go convention)
- Unit tests: mock repository interfaces using `testify/mock`
- Integration tests: real Postgres + Redis via build tags (`//go:build integration`)
- `go test ./...` runs unit tests by default
- `go test -tags integration ./...` runs integration tests
- Test helpers in `internal/testutil/`

---

## Golang Coding Conventions

Per project golang-skill:
- camelCase unexported, PascalCase exported, `-er` suffix for single-method interfaces
- No `utils/helpers/common` packages
- Early return error handling, no nesting, no panics
- Always use `context.Context` for IO operations
- WaitGroup for goroutines, check `ctx.Done()` for cancellation
- Keep files small, split by domain

---

## Dependency Injection

Manual constructor injection. All constructors accept `context.Context` where needed for IO. Each layer receives its dependencies via constructor:

```go
repo := repository.NewUserPostgres(db)
jwtSvc := security.NewJWTService(cfg.JWT)
hasher := security.NewBcryptHasher()
authSvc := service.NewAuth(repo, jwtSvc, hasher, redisClient, cfg.Auth)
userSvc := service.NewUsers(repo)
authHandler := handlers.NewAuth(authSvc)
userHandler := handlers.NewUsers(userSvc)
healthHandler := handlers.NewHealth(db, redisClient)
```

Wired in `cmd/server/main.go`.
