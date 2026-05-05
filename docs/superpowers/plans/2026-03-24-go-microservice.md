# Go Microservice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade Go microservice template with Fiber, GORM, multi-DB support, JWT auth, and structured logging — mirroring the FastAPI microservice.

**Architecture:** Layered clean architecture (handlers → services → repositories) with manual DI, repository interfaces for multi-DB support, and Fiber as the HTTP framework. All code lives in `internal/` with entry point in `cmd/server/`.

**Tech Stack:** Go 1.22+, Fiber v2, GORM, golang-migrate, zerolog, go-redis/v9, golang-jwt/v5, bcrypt, Viper, testify

**Spec:** `docs/superpowers/specs/2026-03-24-go-microservice-design.md`

**Target directory:** `/Users/the_elita/Desktop/apps/github/go-microservice`

---

## File Map

### cmd/
- `cmd/server/main.go` — Entry point, DI wiring, graceful shutdown

### internal/config/
- `internal/config/config.go` — Viper-based config struct, env loading, validation

### internal/logger/
- `internal/logger/logger.go` — zerolog setup, request-scoped logging

### internal/domain/errors/
- `internal/domain/errors/api.go` — HTTP error types with error envelope
- `internal/domain/errors/repository.go` — Data access error sentinels
- `internal/domain/errors/service.go` — Business logic error sentinels

### internal/domain/models/
- `internal/domain/models/user.go` — GORM User model with hooks

### internal/domain/dto/
- `internal/domain/dto/auth.go` — Auth request/response DTOs
- `internal/domain/dto/users.go` — User CRUD DTOs
- `internal/domain/dto/pagination.go` — Pagination DTOs

### internal/db/
- `internal/db/postgres.go` — Postgres GORM connection
- `internal/db/mysql.go` — MySQL GORM connection
- `internal/db/mongo.go` — MongoDB connection
- `internal/db/redis.go` — Redis client
- `internal/db/factory.go` — DB provider factory
- `internal/db/migrate.go` — Embedded migrations runner
- `internal/db/migrations/000001_init.up.sql` — Initial schema
- `internal/db/migrations/000001_init.down.sql` — Rollback

### internal/repository/
- `internal/repository/interfaces.go` — UserRepository interface
- `internal/repository/user_postgres.go` — Postgres implementation
- `internal/repository/user_postgres_test.go` — Integration tests
- `internal/repository/user_mysql.go` — MySQL implementation
- `internal/repository/user_mongo.go` — MongoDB implementation

### internal/security/
- `internal/security/interfaces.go` — Hasher + TokenService interfaces
- `internal/security/hasher.go` — bcrypt Hasher
- `internal/security/hasher_test.go` — Hasher unit tests
- `internal/security/jwt.go` — JWT TokenService
- `internal/security/jwt_test.go` — JWT unit tests

### internal/service/
- `internal/service/users.go` — User CRUD + pagination
- `internal/service/users_test.go` — Unit tests with mocked repo
- `internal/service/auth.go` — Auth logic, brute-force protection
- `internal/service/auth_test.go` — Unit tests with mocked deps

### internal/api/middleware/
- `internal/api/middleware/request_id.go` — X-Request-ID
- `internal/api/middleware/timing.go` — X-Process-Time + slow logging
- `internal/api/middleware/security_headers.go` — Security headers
- `internal/api/middleware/trusted_host.go` — Host validation
- `internal/api/middleware/cors.go` — CORS config
- `internal/api/middleware/rate_limiter.go` — Redis + in-memory rate limiting
- `internal/api/middleware/error_handler.go` — Error envelope handler
- `internal/api/middleware/auth.go` — JWT auth middleware
- `internal/api/middleware/rate_limiter_test.go` — Rate limiter tests
- `internal/api/middleware/trusted_host_test.go` — Trusted host tests
- `internal/api/middleware/auth_test.go` — Auth middleware tests

### internal/api/handlers/
- `internal/api/handlers/health.go` — Health endpoints
- `internal/api/handlers/health_test.go` — Health unit tests
- `internal/api/handlers/auth.go` — Auth endpoints
- `internal/api/handlers/auth_test.go` — Auth handler tests
- `internal/api/handlers/users.go` — User CRUD endpoints
- `internal/api/handlers/users_test.go` — User handler tests

### internal/api/
- `internal/api/router.go` — Route setup, middleware stack

### infra/
- `infra/Dockerfile` — Multi-stage build
- `infra/docker-compose.local.yml` — All services
- `infra/nginx.conf` — Reverse proxy
- `infra/.env-example` — Example env vars
- `infra/commands/entrypoint.sh` — Container entrypoint
- `infra/commands/migrate.sh` — Migration runner

### root files
- `go.mod` — Module definition
- `.gitignore` — Go gitignore
- `Makefile` — Dev commands
- `.github/workflows/ci.yml` — CI pipeline

---

## Task 1: Project Scaffold & Config

**Files:**
- Create: `go.mod`, `.gitignore`, `Makefile`
- Create: `internal/config/config.go`
- Create: `internal/logger/logger.go`

- [ ] **Step 1: Initialize Go module and create .gitignore**

```bash
cd /Users/the_elita/Desktop/apps/github
mkdir go-microservice && cd go-microservice
go mod init github.com/the_elita/go-microservice
```

Create `.gitignore` with standard Go ignores (binary, vendor, .env, IDE files).

- [ ] **Step 2: Install core dependencies**

```bash
go get github.com/gofiber/fiber/v2
go get github.com/spf13/viper
go get github.com/rs/zerolog
```

- [ ] **Step 3: Write config.go**

Create `internal/config/config.go`:
- Define `Config` struct with nested sub-structs: `ServerConfig` (includes `DBProvider string`), `JWTConfig`, `AuthConfig`, `PostgresConfig`, `MySQLConfig`, `MongoConfig`, `RedisConfig`, `RateLimitConfig` (includes `Enabled bool`), `CORSConfig`, `PaginationConfig`, `LoggingConfig`
- `Load()` function reads from env vars + `.env` file via Viper
- `Validate()` checks: reject wildcard trusted_hosts in production, require JWT secret in non-dev
- Defaults: port 8080, env "development", access_token_expiry 15m, refresh_token_expiry 7d, max_attempts 5, max_per_page 100

- [ ] **Step 4: Write logger.go**

Create `internal/logger/logger.go`:
- `New(cfg LoggingConfig)` returns configured `zerolog.Logger`
- JSON output when env != "development", pretty console otherwise
- Parse log level from config string
- `WithRequestID(logger zerolog.Logger, requestID string)` returns sub-logger with request_id field

- [ ] **Step 5: Create Makefile**

Targets: `run`, `build`, `test`, `test-unit`, `test-integration`, `lint`, `fmt`, `migrate-up`, `migrate-down`, `migrate-create`, `docker-up-postgres`, `docker-up-mysql`, `docker-up-mongo`

- [ ] **Step 6: Verify it compiles**

```bash
go build ./...
```

- [ ] **Step 7: Commit**

```bash
git init
git add -A
git commit -m "feat: project scaffold with config and logger"
```

---

## Task 2: Domain Layer — Errors, Models, DTOs

**Files:**
- Create: `internal/domain/errors/api.go`
- Create: `internal/domain/errors/repository.go`
- Create: `internal/domain/errors/service.go`
- Create: `internal/domain/models/user.go`
- Create: `internal/domain/dto/auth.go`
- Create: `internal/domain/dto/users.go`
- Create: `internal/domain/dto/pagination.go`

- [ ] **Step 1: Write error types**

`internal/domain/errors/repository.go`:
- Sentinel errors: `ErrNotFound`, `ErrCannotCreate`, `ErrCannotUpdate`, `ErrCannotDelete`, `ErrInvalidInput`

`internal/domain/errors/service.go`:
- Sentinel errors: `ErrInvalidCredentials`, `ErrInvalidToken`, `ErrInvalidTokenType`, `ErrLoginLocked`, `ErrUserAlreadyExists`, `ErrUserNotFound`, `ErrInvalidInput`

`internal/domain/errors/api.go`:
- `APIError` struct: `Type string`, `Message string`, `StatusCode int`, `RequestID string`
- Implements `error` interface
- `ErrorResponse` struct: `Error ErrorBody` for JSON envelope
- `ErrorBody` struct: `Type`, `Message`, `RequestID`
- Constructor helpers: `NewUnauthorized()`, `NewNotFound()`, `NewBadRequest()`, `NewConflict()`, `NewTooManyRequests(retryAfter)`, `NewInternal()`

- [ ] **Step 2: Write User model**

`internal/domain/models/user.go`:
- `User` struct with GORM tags: `ID uint`, `CreatedAt time.Time`, `UpdatedAt time.Time`, `DeletedAt gorm.DeletedAt` (soft delete index), `Email string` (uniqueIndex), `HashedPassword string`
- `BeforeCreate` hook: lowercase email
- `BeforeUpdate` hook: lowercase email
- `TableName()` returns `"users"`

- [ ] **Step 3: Write DTOs**

`internal/domain/dto/auth.go`:
- `RegisterRequest`: Email, Password (json tags)
- `LoginRequest`: Email, Password
- `RefreshRequest`: RefreshToken
- `TokenResponse`: AccessToken, RefreshToken, TokenType ("bearer")
- `UserResponse`: ID, Email, CreatedAt

`internal/domain/dto/users.go`:
- `CreateUserRequest`: Email, Password
- `UpdateUserRequest`: Email *string, Password *string (pointer = optional)
- `UserResponse`: ID, Email, CreatedAt, UpdatedAt
- `DeleteResponse`: Status, ID

`internal/domain/dto/pagination.go`:
- `PaginationRequest`: Page int, PerPage int (defaults: 1, 20)
- `PaginationMeta`: TotalPages, CurrentPage, TotalItems, HasNext, HasPrevious
- `PaginatedResponse[T any]`: Items []T, Meta PaginationMeta

- [ ] **Step 4: Verify it compiles**

```bash
go build ./...
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: domain layer — errors, user model, DTOs"
```

---

## Task 3: Database Layer

**Files:**
- Create: `internal/db/postgres.go`
- Create: `internal/db/mysql.go`
- Create: `internal/db/mongo.go`
- Create: `internal/db/redis.go`
- Create: `internal/db/factory.go`
- Create: `internal/db/migrate.go`
- Create: `internal/db/migrations/000001_init.up.sql`
- Create: `internal/db/migrations/000001_init.down.sql`

- [ ] **Step 1: Install DB dependencies**

```bash
go get gorm.io/gorm
go get gorm.io/driver/postgres
go get gorm.io/driver/mysql
go get go.mongodb.org/mongo-driver/mongo
go get github.com/redis/go-redis/v9
go get github.com/golang-migrate/migrate/v4
```

- [ ] **Step 2: Write postgres.go**

- `NewPostgres(ctx context.Context, cfg PostgresConfig) (*gorm.DB, error)`
- Configure connection pool: `MaxOpenConns`, `MaxIdleConns`, `ConnMaxLifetime`
- Ping to verify connection

- [ ] **Step 3: Write mysql.go**

- `NewMySQL(ctx context.Context, cfg MySQLConfig) (*gorm.DB, error)`
- Same pool config pattern as postgres

- [ ] **Step 4: Write mongo.go**

- `NewMongo(ctx context.Context, cfg MongoConfig) (*mongo.Database, error)`
- Connect with URI, ping, return database handle

- [ ] **Step 5: Write redis.go**

- `NewRedis(ctx context.Context, cfg RedisConfig) (*redis.Client, error)`
- Connect, ping, return client
- If ping fails, log warning and return nil (graceful fallback)

- [ ] **Step 6: Write factory.go**

- `NewDatabase(ctx context.Context, cfg Config) (*gorm.DB, error)` — switch on `cfg.Server.DBProvider`
- Returns error for unknown provider
- MongoDB handled separately (not GORM) — factory also exports `NewMongoDatabase`

- [ ] **Step 7: Write migrations**

`internal/db/migrations/000001_init.up.sql`:
```sql
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    CONSTRAINT users_email_lower CHECK (email = LOWER(email))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users (LOWER(email)) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at);
```

`internal/db/migrations/000001_init.down.sql`:
```sql
DROP TABLE IF EXISTS users;
```

- [ ] **Step 8: Write migrate.go**

- `//go:embed migrations/*.sql` for embedding
- `RunMigrations(dbURL string) error` — creates migrate instance from embedded FS, runs Up
- Handles `migrate.ErrNoChange` gracefully
- Note: SQL migrations are Postgres-specific. MySQL uses GORM AutoMigrate as fallback. MongoDB is schemaless.

- [ ] **Step 9: Verify it compiles**

```bash
go build ./...
```

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "feat: database layer — postgres, mysql, mongo, redis, migrations"
```

---

## Task 4: Security Layer

**Files:**
- Create: `internal/security/interfaces.go`
- Create: `internal/security/hasher.go`
- Create: `internal/security/hasher_test.go`
- Create: `internal/security/jwt.go`
- Create: `internal/security/jwt_test.go`

- [ ] **Step 1: Install dependencies**

```bash
go get github.com/golang-jwt/jwt/v5
go get golang.org/x/crypto/bcrypt
go get github.com/stretchr/testify
```

- [ ] **Step 2: Write interfaces.go**

```go
type Hasher interface {
    Hash(password string) (string, error)
    Verify(password, hash string) error  // nil = match, non-nil = mismatch or failure
}

type TokenService interface {
    GenerateAccessToken(userID uint, email string) (string, error)
    GenerateRefreshToken(userID uint, email string) (string, error)
    ValidateToken(tokenString string) (*Claims, error)
}

type Claims struct {
    UserID    uint   `json:"user_id"`
    Email     string `json:"email"`
    TokenType string `json:"token_type"`
    jwt.RegisteredClaims
}
```

- [ ] **Step 3: Write failing hasher tests**

`internal/security/hasher_test.go`:
- `TestHash_ReturnsHashedString` — hash is not empty and differs from input
- `TestVerify_CorrectPassword` — returns nil
- `TestVerify_WrongPassword` — returns error

Run: `go test ./internal/security/ -run TestHash -v`
Expected: FAIL (no implementation)

- [ ] **Step 4: Write hasher.go implementation**

- `BcryptHasher` struct implementing `Hasher`
- `NewBcryptHasher() *BcryptHasher`
- `Hash()` uses `bcrypt.GenerateFromPassword` with `bcrypt.DefaultCost`
- `Verify()` uses `bcrypt.CompareHashAndPassword`

Run: `go test ./internal/security/ -run TestHash -v && go test ./internal/security/ -run TestVerify -v`
Expected: PASS

- [ ] **Step 5: Write failing JWT tests**

`internal/security/jwt_test.go`:
- `TestGenerateAccessToken_ValidClaims` — decode token, check user_id, email, token_type="access"
- `TestGenerateRefreshToken_ValidClaims` — token_type="refresh"
- `TestValidateToken_ExpiredToken` — returns error
- `TestValidateToken_WrongTokenType` — generate refresh token, call ValidateToken, assert claims.TokenType != "access"

Run: `go test ./internal/security/ -run TestGenerate -v`
Expected: FAIL

- [ ] **Step 6: Write jwt.go implementation**

- `JWTService` struct with `secretKey`, `accessExpiry`, `refreshExpiry`
- `NewJWTService(cfg JWTConfig) *JWTService`
- `GenerateAccessToken()` — creates signed JWT with claims, token_type="access"
- `GenerateRefreshToken()` — token_type="refresh"
- `ValidateToken()` — parses, validates signature, returns `*Claims`

Run: `go test ./internal/security/ -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: security layer — bcrypt hasher and JWT service with tests"
```

---

## Task 5: Repository Layer

**Files:**
- Create: `internal/repository/interfaces.go`
- Create: `internal/repository/user_postgres.go`
- Create: `internal/repository/user_mysql.go`
- Create: `internal/repository/user_mongo.go`

- [ ] **Step 1: Write interfaces.go**

Define `UserRepository` interface with all methods from spec:
`GetByID`, `GetByEmail`, `GetAll`, `Create`, `Update`, `Delete`, `Restore`, `Count`
All methods take `context.Context` as first param.

- [ ] **Step 2: Write user_postgres.go**

- `PostgresUserRepository` struct with `*gorm.DB`
- `NewUserPostgres(db *gorm.DB) *PostgresUserRepository`
- Implement all interface methods using GORM
- `Delete()` uses GORM soft delete
- `Restore()` uses `db.Unscoped().Model(&User{}).Where("id = ?", id).Update("deleted_at", nil)`
- `GetAll()` with `Limit` and `Offset`
- Map GORM errors to domain errors (e.g., `gorm.ErrRecordNotFound` → `errors.ErrNotFound`)

- [ ] **Step 3: Write user_mysql.go**

- `MySQLUserRepository` struct — nearly identical to postgres
- `NewUserMySQL(db *gorm.DB) *MySQLUserRepository`
- Same GORM operations (GORM abstracts dialect differences)

- [ ] **Step 4: Write user_mongo.go**

- `MongoUserRepository` struct with `*mongo.Collection`
- `NewUserMongo(db *mongo.Database) *MongoUserRepository`
- Uses collection "users"
- Manual ID sequencing via "counters" collection (like FastAPI template)
- `Delete()` sets `deleted_at` field (no GORM soft delete for mongo)
- `GetAll()` filters where `deleted_at` is null
- `Restore()` unsets `deleted_at`

- [ ] **Step 5: Verify it compiles**

```bash
go build ./...
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: repository layer — postgres, mysql, mongo implementations"
```

---

## Task 6: Service Layer

**Files:**
- Create: `internal/service/users.go`
- Create: `internal/service/users_test.go`
- Create: `internal/service/auth.go`
- Create: `internal/service/auth_test.go`

- [ ] **Step 1: Write failing users service tests**

`internal/service/users_test.go`:
- Create mock `UserRepository` using testify/mock
- `TestGetUser_Found` — repo returns user, service returns UserResponse DTO
- `TestGetUser_NotFound` — repo returns ErrNotFound, service returns ErrUserNotFound
- `TestListUsers_WithPagination` — verify limit/offset calculation from page/per_page
- `TestCreateUser_Success` — hashes password, calls repo.Create
- `TestCreateUser_DuplicateEmail` — repo returns ErrCannotCreate, service returns ErrUserAlreadyExists
- `TestDeleteUser_Success` — calls repo.Delete

Run: `go test ./internal/service/ -run TestGetUser -v`
Expected: FAIL

- [ ] **Step 2: Write users.go**

- `UserService` struct with `repo UserRepository`, `hasher Hasher`
- `NewUsers(repo UserRepository, hasher Hasher) *UserService`
- `GetByID(ctx, id)` → `(*dto.UserResponse, error)` — fetch + convert model→DTO
- `List(ctx, page, perPage)` → `(*dto.PaginatedResponse[dto.UserResponse], error)` — calc offset, fetch, count, build meta
- `Create(ctx, req)` → `(*dto.UserResponse, error)` — hash password, create, return DTO
- `Update(ctx, id, req)` → `(*dto.UserResponse, error)` — fetch, update fields, save
- `Delete(ctx, id)` → error — call repo.Delete
- Helper: `userToResponse(model) dto.UserResponse`

Run: `go test ./internal/service/ -run TestGetUser -v && go test ./internal/service/ -run TestListUsers -v`
Expected: PASS

- [ ] **Step 3: Write failing auth service tests**

`internal/service/auth_test.go`:
- Mock repo, hasher, token service, redis client
- `TestRegister_Success` — creates user, returns tokens
- `TestRegister_DuplicateEmail` — returns ErrUserAlreadyExists
- `TestLogin_Success` — verifies password, returns tokens
- `TestLogin_WrongPassword` — returns ErrInvalidCredentials
- `TestLogin_LockedAccount` — redis shows too many attempts, returns ErrLoginLocked
- `TestRefresh_Success` — validates refresh token, returns new access token
- `TestRefresh_InvalidToken` — returns ErrInvalidToken
- `TestGetCurrentUser` — validates access token, returns user

Run: `go test ./internal/service/ -run TestRegister -v`
Expected: FAIL

- [ ] **Step 4: Write auth.go**

- `AuthService` struct with `repo`, `tokenSvc`, `hasher`, `redis`, `cfg AuthConfig`
- `NewAuth(repo, tokenSvc, hasher, redis, cfg) *AuthService`
- `Register(ctx, req)` → `(*dto.TokenResponse, error)` — check duplicate, hash pw, create user, generate tokens
- `Login(ctx, req, clientIP)` → `(*dto.TokenResponse, error)` — check lockout, verify pw, track attempts, generate tokens
- `Refresh(ctx, req)` → `(*dto.TokenResponse, error)` — validate refresh token type, generate new access token
- `GetCurrentUser(ctx, tokenString)` → `(*dto.UserResponse, error)` — validate access token, fetch user
- Private: `checkLoginLock(ctx, email, ip)`, `trackFailedAttempt(ctx, email, ip)`, `clearFailedAttempts(ctx, email, ip)`

Run: `go test ./internal/service/ -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: service layer — users and auth with tests"
```

---

## Task 7: Middleware

**Files:**
- Create: `internal/api/middleware/request_id.go`
- Create: `internal/api/middleware/timing.go`
- Create: `internal/api/middleware/security_headers.go`
- Create: `internal/api/middleware/trusted_host.go`
- Create: `internal/api/middleware/cors.go`
- Create: `internal/api/middleware/rate_limiter.go`
- Create: `internal/api/middleware/error_handler.go`
- Create: `internal/api/middleware/auth.go`

- [ ] **Step 1: Write request_id.go**

- Generate UUID if no `X-Request-ID` header present
- Set `X-Request-ID` on response
- Store in `c.Locals("request_id", id)`

- [ ] **Step 2: Write timing.go**

- Record start time, call `c.Next()`, compute duration
- Set `X-Process-Time` header (milliseconds)
- Log warning if duration > `slow_request_threshold_ms`

- [ ] **Step 3: Write security_headers.go**

- Set: `Strict-Transport-Security`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`
- Remove: `Server`, `X-Powered-By`

- [ ] **Step 4: Write trusted_host.go**

- Check `Host` header against `cfg.Server.TrustedHosts` slice
- If empty slice, allow all (development mode)
- Return 421 Misdirected Request for untrusted hosts

- [ ] **Step 5: Write cors.go**

- Use Fiber's built-in `cors` middleware configured from `cfg.CORS`
- Set AllowOrigins, AllowMethods, AllowCredentials

- [ ] **Step 6: Write rate_limiter.go**

- `RateLimiter` struct with redis client and in-memory map fallback
- `New(redis, cfg)` constructor
- If `cfg.RateLimit.Enabled` is false, return a no-op middleware (pass through)
- Middleware function: extract client IP, check rate based on method (GET vs POST/PUT/DELETE)
- Redis: INCR key with TTL = time window (time_get for GET, time_ppd for POST/PUT/DELETE)
- Fallback: `sync.Map` with atomic counters when redis is nil
- Return 429 with `Retry-After` header when exceeded

- [ ] **Step 7: Write error_handler.go**

- Fiber `ErrorHandler` function
- Check if error is `*domain.APIError` → use its status code and type
- Check if error is `*fiber.Error` → map to appropriate type
- Default: 500 Internal Server Error
- Always return JSON envelope: `{"error": {"type": "...", "message": "...", "request_id": "..."}}`

- [ ] **Step 8: Write auth.go middleware**

- Extract `Authorization: Bearer <token>` header
- Call `tokenSvc.ValidateToken(token)` — check token_type is "access"
- Set claims in `c.Locals("claims", claims)` (user_id, email from JWT)
- Handler layer fetches full user from DB if needed — middleware only validates token
- Return 401 on any failure

- [ ] **Step 9: Write middleware tests**

`internal/api/middleware/rate_limiter_test.go`:
- `TestRateLimiter_AllowsUnderLimit` — send requests under limit, all return 200
- `TestRateLimiter_BlocksOverLimit` — exceed limit, returns 429 with Retry-After
- `TestRateLimiter_InMemoryFallback` — redis=nil, still rate limits with in-memory counters
- `TestRateLimiter_SkipsWhenDisabled` — cfg.Enabled=false, no rate limiting

`internal/api/middleware/trusted_host_test.go`:
- `TestTrustedHost_AllowsValidHost` — Host in whitelist → passes through
- `TestTrustedHost_RejectsInvalidHost` — Host not in whitelist → 421
- `TestTrustedHost_AllowsAllWhenEmpty` — empty whitelist → passes through

`internal/api/middleware/auth_test.go`:
- `TestAuth_ValidToken` — valid Bearer token → sets claims in Locals
- `TestAuth_MissingHeader` — no Authorization → 401
- `TestAuth_InvalidToken` — bad token → 401

Run: `go test ./internal/api/middleware/ -v`
Expected: ALL PASS

- [ ] **Step 10: Verify it compiles**

```bash
go build ./...
```

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "feat: middleware stack — request ID, timing, security headers, CORS, rate limiter, auth with tests"
```

---

## Task 8: Handlers & Router

**Files:**
- Create: `internal/api/handlers/health.go`
- Create: `internal/api/handlers/health_test.go`
- Create: `internal/api/handlers/auth.go`
- Create: `internal/api/handlers/auth_test.go`
- Create: `internal/api/handlers/users.go`
- Create: `internal/api/handlers/users_test.go`
- Create: `internal/api/router.go`

- [ ] **Step 1: Write failing health handler tests**

`internal/api/handlers/health_test.go`:
- `TestHealthEndpoint` — returns 200 with status
- `TestLiveEndpoint` — returns 200
- `TestReadyEndpoint_AllHealthy` — returns 200 "ready"
- `TestRootEndpoint` — returns 200 with app name and version

Run: `go test ./internal/api/handlers/ -run TestHealth -v`
Expected: FAIL

- [ ] **Step 2: Write health.go**

- `HealthHandler` struct with `db *gorm.DB`, `redis *redis.Client`
- `NewHealth(db, redis) *HealthHandler`
- `Health(c)` — `{"status": "ok"}`
- `Live(c)` — `{"status": "alive"}`
- `Ready(c)` — ping DB and Redis, return "ready"/"degraded" based on results
- `Root(c)` — `{"app": cfg.AppName, "version": cfg.AppVersion, "status": "running"}`

Run: `go test ./internal/api/handlers/ -run TestHealth -v`
Expected: PASS

- [ ] **Step 3: Write failing auth handler tests**

`internal/api/handlers/auth_test.go`:
- Mock auth service
- `TestRegister_Success` — POST /api/v1/auth/register with valid body → 201 + tokens
- `TestRegister_InvalidBody` — missing email → 400
- `TestLogin_Success` — POST /api/v1/auth/login → 200 + tokens
- `TestLogin_InvalidCredentials` — → 401
- `TestRefresh_Success` — POST /api/v1/auth/refresh → 200 + new token
- `TestMe_Authenticated` — GET /api/v1/auth/me with valid token → 200 + user

Run: `go test ./internal/api/handlers/ -run TestRegister -v`
Expected: FAIL

- [ ] **Step 4: Write auth.go handler**

- Define `AuthServicer` interface in handler package (accepted interface pattern):
  `Register(ctx, req)`, `Login(ctx, req, ip)`, `Refresh(ctx, req)`, `GetCurrentUser(ctx, userID)`
- `AuthHandler` struct with `svc AuthServicer`
- `NewAuth(svc AuthServicer) *AuthHandler`
- `Register(c)` — parse body, call svc.Register, return 201
- `Login(c)` — parse body, call svc.Login with c.IP(), return 200
- `Refresh(c)` — parse body, call svc.Refresh, return 200
- `Me(c)` — get user from c.Locals("user"), return 200
- Map service errors to API errors (ErrUserAlreadyExists→409, ErrInvalidCredentials→401, etc.)

Run: `go test ./internal/api/handlers/ -run TestRegister -v && go test ./internal/api/handlers/ -run TestLogin -v`
Expected: PASS

- [ ] **Step 5: Write failing users handler tests**

`internal/api/handlers/users_test.go`:
- Mock user service
- `TestListUsers_Paginated` — GET /api/v1/users?page=1&per_page=10 → 200 + paginated response
- `TestGetUser_Found` — GET /api/v1/users/1 → 200
- `TestGetUser_NotFound` — GET /api/v1/users/999 → 404
- `TestCreateUser_Success` — POST /api/v1/users → 201
- `TestUpdateUser_Success` — PATCH /api/v1/users/1 → 200
- `TestDeleteUser_Success` — DELETE /api/v1/users/1 → 200 + `{"status": "success", "id": 1}`

Run: `go test ./internal/api/handlers/ -run TestListUsers -v`
Expected: FAIL

- [ ] **Step 6: Write users.go handler**

- Define `UserServicer` interface in handler package:
  `GetByID(ctx, id)`, `List(ctx, page, perPage)`, `Create(ctx, req)`, `Update(ctx, id, req)`, `Delete(ctx, id)`
- `UserHandler` struct with `svc UserServicer`
- `NewUsers(svc UserServicer) *UserHandler`
- `List(c)` — parse page/per_page query params (default 1/20), call svc.List, return 200
- `Get(c)` — parse :id param, call svc.GetByID, return 200
- `Create(c)` — parse body, call svc.Create, return 201
- `Update(c)` — parse :id + body, call svc.Update, return 200
- `Delete(c)` — parse :id, call svc.Delete, return 200 + delete response

Run: `go test ./internal/api/handlers/ -v`
Expected: ALL PASS

- [ ] **Step 7: Write router.go**

- `SetupRouter(app *fiber.App, handlers, middleware, cfg)` function
- Register middleware in order: RequestID, Timing, SecurityHeaders, TrustedHost, CORS, RateLimiter
- Set custom error handler
- Mount routes:
  - `GET /` → health.Root
  - `GET /health` → health.Health
  - `GET /live` → health.Live
  - `GET /ready` → health.Ready
  - `/api/v1/auth` group: register, login, refresh, me (me uses auth middleware)
  - `/api/v1/users` group (all with auth middleware): list, get, create, update, delete

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: handlers and router — health, auth, users endpoints with tests"
```

---

## Task 9: Main Entry Point

**Files:**
- Create: `cmd/server/main.go`

- [ ] **Step 1: Write main.go**

- Load config via `config.Load()`
- Initialize logger via `logger.New(cfg.Logging)`
- Connect database via `db.NewDatabase(ctx, cfg)`
- Run migrations via `db.RunMigrations(cfg.Postgres.DSN)` (if postgres)
- Connect Redis via `db.NewRedis(ctx, cfg.Redis)`
- Wire all dependencies:
  - `repo` → from factory based on provider
  - `hasher` → `security.NewBcryptHasher()`
  - `jwtSvc` → `security.NewJWTService(cfg.JWT)`
  - `authSvc` → `service.NewAuth(repo, jwtSvc, hasher, redis, cfg.Auth)`
  - `userSvc` → `service.NewUsers(repo, hasher)`
  - handlers → from services
  - middleware → from config + redis
- Create Fiber app with custom error handler
- Setup router
- Graceful shutdown: listen for SIGINT/SIGTERM, close app, DB, Redis
- Start server on `cfg.Server.Host:cfg.Server.Port`

- [ ] **Step 2: Verify it compiles and runs**

```bash
go build -o bin/server ./cmd/server
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: main entry point with DI wiring and graceful shutdown"
```

---

## Task 10: Infrastructure

**Files:**
- Create: `infra/Dockerfile`
- Create: `infra/docker-compose.local.yml`
- Create: `infra/nginx.conf`
- Create: `infra/.env-example`
- Create: `infra/commands/entrypoint.sh`
- Create: `infra/commands/migrate.sh`

- [ ] **Step 1: Write Dockerfile**

Multi-stage:
```dockerfile
# Builder
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /bin/server ./cmd/server

# Production
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
RUN adduser -D -u 1000 appuser
COPY --from=builder /bin/server /bin/server
USER appuser
EXPOSE 8080
CMD ["/bin/server"]
```

- [ ] **Step 2: Write docker-compose.local.yml**

Services:
- `api`: Go service, port 8080, depends on redis, env_file, health check
- `postgres`: postgres:17, port 5432, volume, health check, profile "postgres"
- `mysql`: mysql:8.4, port 3306, volume, health check, profile "mysql"
- `mongo`: mongo:7, port 27017, volume, health check, profile "mongo"
- `redis`: redis:7-alpine, port 6379, health check
- `nginx`: nginx:alpine, port 80, depends on api

- [ ] **Step 3: Write nginx.conf**

Upstream `api` pointing to `api:8080`. Proxy pass all traffic.

- [ ] **Step 4: Write .env-example**

All config keys with sensible defaults and comments.

- [ ] **Step 5: Write entrypoint.sh and migrate.sh**

`entrypoint.sh`: run migrations then start server.
`migrate.sh`: run golang-migrate up.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: infrastructure — Dockerfile, docker-compose, nginx, env"
```

---

## Task 11: CI Pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write ci.yml**

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: Install golangci-lint
        run: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
      - name: Lint
        run: golangci-lint run ./...
      - name: Unit Tests
        run: go test ./... -v -count=1
      - name: Integration Tests
        run: go test -tags integration ./... -v -count=1
        env:
          DB_PROVIDER: postgres
          POSTGRES_DSN: "host=localhost port=5432 user=test password=test dbname=test_db sslmode=disable"
          REDIS_HOST: localhost
          REDIS_PORT: "6379"
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "ci: GitHub Actions pipeline with postgres, redis, lint, tests"
```

---

## Task 12: Integration Tests & Final Verification

**Files:**
- Create: `internal/repository/user_postgres_test.go`
- Create: `internal/testutil/testutil.go`

- [ ] **Step 1: Write test helpers**

`internal/testutil/testutil.go`:
- `SetupTestDB(t *testing.T) *gorm.DB` — connect to test postgres, auto-migrate User model, return db
- `CleanupTestDB(t *testing.T, db *gorm.DB)` — truncate users table
- `SetupTestRedis(t *testing.T) *redis.Client` — connect to test redis

- [ ] **Step 2: Write postgres repository integration tests**

`internal/repository/user_postgres_test.go` (with `//go:build integration`):
- `TestCreateUser_Integration` — create user, verify in DB
- `TestGetByEmail_Integration` — create then fetch by email
- `TestGetAll_Pagination_Integration` — create 5 users, fetch with limit 2 offset 0
- `TestSoftDelete_Integration` — delete user, verify GetByID returns not found, verify Restore works
- `TestCount_Integration` — create N users, verify count

Run: `go test -tags integration ./internal/repository/ -v`
Expected: ALL PASS (requires running postgres)

- [ ] **Step 3: Run full test suite**

```bash
go test ./... -v -count=1
go vet ./...
```

Expected: ALL PASS

- [ ] **Step 4: Run the server manually**

```bash
# Start postgres + redis via docker-compose
# Then:
go run ./cmd/server
# In another terminal:
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/live
```

Expected: JSON responses from all endpoints

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: integration tests and test utilities"
```

---

## Summary

| Task | Description | Depends On |
|------|-------------|------------|
| 1 | Project scaffold, config, logger | — |
| 2 | Domain: errors, models, DTOs | 1 |
| 3 | Database layer: connections, factory, migrations | 1, 2 |
| 4 | Security: hasher, JWT (with tests) | 1, 2 |
| 5 | Repository: interfaces + implementations | 2, 3 |
| 6 | Service: users + auth (with tests) | 4, 5 |
| 7 | Middleware stack (with tests) | 1, 2, 4 |
| 8 | Handlers + router (with tests) | 6, 7 |
| 9 | Main entry point with DI | all above |
| 10 | Infrastructure: Docker, compose, nginx | 9 |
| 11 | CI pipeline | 9 |
| 12 | Integration tests + verification | all above |
