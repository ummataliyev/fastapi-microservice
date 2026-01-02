# FastAPI Microservice

A production-ready FastAPI microservice template with comprehensive features for building scalable and maintainable APIs.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Development Commands](#development-commands)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Security](#security)
- [Contributing](#contributing)

## ✨ Features

### Core Features
- **FastAPI Framework** - Modern, fast (high-performance) web framework for building APIs with Python 3.11+
- **PostgreSQL Database** - Robust relational database with SQLAlchemy ORM
- **Redis Integration** - Caching and message broker support
- **JWT Authentication** - Secure token-based authentication system
- **WebSocket Support** - Real-time bidirectional communication

### Architecture & Patterns
- **Clean Architecture** - Separation of concerns with layered structure
- **Repository Pattern** - Data access abstraction layer
- **Service Layer** - Business logic encapsulation
- **Dependency Injection** - FastAPI's built-in DI system
- **Database Mixins** - Reusable model behaviors (timestamps, soft deletion, primary keys)
- **Mapper Pattern** - Data transformation between layers

### Developer Experience
- **Docker Support** - Containerized development and deployment
- **Database Migrations** - Alembic for version-controlled schema changes
- **Poetry & UV** - Modern dependency management
- **Testing Suite** - Unit and integration tests with pytest
- **Factory Pattern** - Test data generation with factories
- **Makefile** - Common development commands
- **Code Quality** - Ruff for linting and formatting

### Production Ready
- **Error Handling** - Centralized exception handling middleware
- **Rate Limiting** - API throttling and request limiting
- **Circuit Breaker** - Resilience pattern for external service calls
- **Retry Logic** - Automatic retry mechanisms with exponential backoff
- **CORS Middleware** - Cross-origin resource sharing configuration
- **Request ID Tracking** - Request tracing for debugging
- **Response Timing** - Performance monitoring middleware
- **Observability** - Structured logging system
- **Nginx** - Reverse proxy configuration

### Advanced Features
- **Pagination Support** - Efficient data pagination with configurable limits
- **HTTP Client** - Configured client for external API calls
- **Transaction Management** - Database transaction handling and rollback
- **Security Implementations** - Bcrypt password hashing, JWT token service
- **OpenAPI Documentation** - Auto-generated interactive API documentation
- **WebSocket Manager** - Connection management for real-time features

## 📁 Project Structure

```
fastapi-microservice/
├── src/
│   ├── api/                           # API Layer - Route handlers
│   │   ├── dependencies/              # Route dependencies (auth, db, pagination)
│   │   ├── auth.py                    # Authentication endpoints
│   │   ├── users.py                   # User CRUD endpoints
│   │   └── ws.py                      # WebSocket endpoints
│   │
│   ├── core/                          # Core Functionality
│   │   ├── config.py                  # Configuration management
│   │   ├── database.py                # Database connection setup
│   │   ├── http_client.py             # HTTP client configuration
│   │   ├── jwt.py                     # JWT utilities
│   │   ├── pagination.py              # Pagination helpers
│   │   ├── rate_limit.py              # Rate limiting configuration
│   │   ├── redis.py                   # Redis client setup
│   │   ├── settings.py                # Application settings
│   │   ├── observability/             # Logging and monitoring
│   │   │   └── logging.py
│   │   ├── resilience/                # Resilience patterns
│   │   │   ├── circuit_breaker.py
│   │   │   └── retry.py
│   │   └── throttle/                  # Rate limiting implementation
│   │       └── limiter.py
│   │
│   ├── db/                            # Database Configuration
│   │   ├── postgres/                  # PostgreSQL setup
│   │   │   ├── database.py
│   │   │   └── mixins/                # Reusable model mixins
│   │   │       ├── pk.py              # Primary key mixin
│   │   │       ├── softdeletion.py    # Soft delete mixin
│   │   │       └── timestamp.py       # Timestamp mixin
│   │   └── redis/                     # Redis broker
│   │       └── broker.py
│   │
│   ├── models/                        # SQLAlchemy Models
│   │   └── users.py                   # User database model
│   │
│   ├── schemas/                       # Pydantic Schemas
│   │   ├── auth.py                    # Authentication schemas
│   │   ├── base.py                    # Base schema classes
│   │   ├── pagination.py              # Pagination schemas
│   │   └── users.py                   # User schemas
│   │
│   ├── repositories/                  # Repository Layer - Data Access
│   │   ├── base.py                    # Base repository with CRUD operations
│   │   └── users.py                   # User repository
│   │
│   ├── services/                      # Service Layer - Business Logic
│   │   ├── base.py                    # Base service class
│   │   ├── auth.py                    # Authentication service
│   │   └── users.py                   # User service
│   │
│   ├── managers/                      # Request/Transaction Managers
│   │   ├── auth.py                    # Authentication manager
│   │   ├── base.py                    # Base manager
│   │   ├── middleware.py              # Middleware manager
│   │   ├── transaction.py             # Transaction manager
│   │   └── websocket.py               # WebSocket connection manager
│   │
│   ├── mappers/                       # Data Transformation
│   │   ├── base.py                    # Base mapper
│   │   └── users.py                   # User data mapper
│   │
│   ├── middlewares/                   # Custom Middleware
│   │   ├── cors.py                    # CORS configuration
│   │   ├── error_handler.py           # Global error handling
│   │   ├── request_id.py              # Request ID tracking
│   │   └── timing.py                  # Response time tracking
│   │
│   ├── security/                      # Security Layer
│   │   ├── exceptions/                # Security exceptions
│   │   │   └── token.py
│   │   ├── implementations/           # Security implementations
│   │   │   ├── bcrypt_hasher.py       # Password hashing
│   │   │   └── jwt_service.py         # JWT token handling
│   │   └── interfaces/                # Security interfaces
│   │       ├── hasher.py              # Password hasher interface
│   │       └── token.py               # Token service interface
│   │
│   ├── exceptions/                    # Custom Exceptions
│   │   ├── api/                       # API layer exceptions
│   │   ├── repository/                # Repository layer exceptions
│   │   ├── schema/                    # Schema validation exceptions
│   │   └── service/                   # Service layer exceptions
│   │
│   ├── integrations/                  # External Integrations
│   │   └── base/                      # Base integration classes
│   │
│   ├── migrations/                    # Alembic Migrations
│   │   ├── env.py                     # Migration environment
│   │   ├── script.py.mako             # Migration template
│   │   └── versions/                  # Migration versions
│   │
│   ├── tests/                         # Test Suite
│   │   ├── conftest.py                # Pytest configuration
│   │   ├── factories/                 # Test data factories
│   │   │   └── users.py
│   │   ├── integration/               # Integration tests
│   │   │   ├── base/                  # Base test classes
│   │   │   └── test_users_api.py
│   │   └── unit/                      # Unit tests
│   │       ├── base/                  # Base test classes
│   │       └── test_users_service.py
│   │
│   ├── enums/                         # Enumerations
│   └── main.py                        # Application entry point
│
├── infra/                             # Infrastructure
│   ├── Dockerfile                     # Docker container definition
│   ├── docker-compose.local.yml       # Docker Compose for local development
│   ├── nginx.conf                     # Nginx configuration
│   └── commands/                      # Docker commands
│       ├── api.sh                     # API startup script
│       └── entrypoint.sh              # Container entrypoint
│
├── docs/                              # Documentation
│   └── openapi.json                   # OpenAPI specification
│
├── alembic.ini                        # Alembic configuration
├── pyproject.toml                     # Project dependencies (Poetry)
├── poetry.lock                        # Locked dependencies
├── uv.lock                            # UV lock file
├── pytest.ini                         # Pytest configuration
├── makefile                           # Development commands
└── README.md                          # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 14+**
- **Redis 6+**
- **Docker & Docker Compose** (optional, but recommended)
- **Poetry** or **UV** (for dependency management)

### Installation

#### Option 1: Using Docker (Recommended)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd fastapi-microservice
```

2. **Build and start all services:**
```bash
make up
```

This will start:
- FastAPI application
- PostgreSQL database
- Redis
- Nginx (reverse proxy)

3. **Apply database migrations:**
```bash
make upgrade
```

4. **Access the application:**
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

#### Option 2: Local Development

1. **Clone the repository:**
```bash
git clone <repository-url>
cd fastapi-microservice
```

2. **Install dependencies:**

Using Poetry:
```bash
poetry install
poetry shell
```

Using UV:
```bash
uv sync
```

3. **Set up environment variables:**

Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
DEBUG=true
ENVIRONMENT=development
API_VERSION=v1
```

4. **Start PostgreSQL and Redis:**
```bash
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:14
docker run -d -p 6379:6379 redis:6
```

5. **Run migrations:**
```bash
alembic upgrade head
```

6. **Start the application:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## ⚙️ Configuration

Configuration is managed through environment variables and the `src/core/config.py` and `src/core/settings.py` modules.

### Key Configuration Areas

- **Database**: Connection string, pool size, echo mode
- **Redis**: Connection URL, key prefix
- **JWT**: Secret key, algorithm, token expiration
- **CORS**: Allowed origins, methods, headers
- **Rate Limiting**: Request limits per endpoint
- **Logging**: Log level, format, handlers
- **Circuit Breaker**: Failure threshold, timeout, recovery

## 🗄️ Database Migrations

This project uses Alembic for database migrations.

### Common Migration Commands

```bash
# Create a new migration
make revision
# You'll be prompted to enter a migration message

# Apply all pending migrations
make upgrade

# Rollback one migration
alembic downgrade -1

# Show current migration status
alembic current

# View migration history
alembic history
```

### Creating Migrations Manually

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description of changes"
```

## 🧪 Testing

The project includes comprehensive unit and integration tests.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test TEST_ARGS="--cov=src --cov-report=html"

# Run specific test file
make test TEST_ARGS="tests/unit/test_users_service.py"

# Run specific test
make test TEST_ARGS="tests/unit/test_users_service.py::TestUserService::test_create_user"

# Run with verbose output
make test TEST_ARGS="-v"

# Run integration tests only
make test TEST_ARGS="tests/integration/"
```

### Test Structure

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test API endpoints and full request/response cycle
- **Factories** (`tests/factories/`): Generate test data using factory pattern
- **Base Test Classes**: Reusable test utilities and fixtures

## 🛠️ Development Commands

The project includes a comprehensive Makefile for common development tasks.

### Available Commands

```bash
# Docker Operations
make up              # Build and start all services
make down            # Stop all services
make restart         # Restart API container
make build           # Build Docker images
make clean           # Remove all containers & volumes

# Database Operations
make upgrade         # Apply all database migrations
make revision        # Create new migration (prompts for message)
make psql            # Connect to PostgreSQL database

# Development
make shell           # Open bash shell in API container
make logs            # Show container logs

# Testing & Code Quality
make test            # Run tests (use TEST_ARGS for pytest options)
make lint            # Run Ruff linter
make format          # Auto-format code with Ruff

# Help
make                 # Show all available commands
```

### Example Workflows

**Start development environment:**
```bash
make up
make upgrade
make logs
```

**Create a new migration:**
```bash
make revision
# Enter: "add user profile fields"
```

**Run tests with coverage:**
```bash
make test TEST_ARGS="--cov=src --cov-report=term-missing"
```

**Format and lint code:**
```bash
make format
make lint
```

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API exploration
  - Try out endpoints directly
  - View request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation interface
  - Better for reading and reference

- **OpenAPI JSON**: http://localhost:8000/openapi.json
  - Raw OpenAPI specification
  - Can be imported into tools like Postman

### Example API Endpoints

```
POST   /api/v1/auth/register    # Register new user
POST   /api/v1/auth/login       # Login and get tokens
POST   /api/v1/auth/refresh     # Refresh access token
GET    /api/v1/users/           # List users (paginated)
POST   /api/v1/users/           # Create user
GET    /api/v1/users/{id}       # Get user by ID
PUT    /api/v1/users/{id}       # Update user
DELETE /api/v1/users/{id}       # Delete user
WS     /ws                      # WebSocket connection
```

## 🏗️ Architecture

### Layered Architecture

The application follows clean architecture principles with clear separation of concerns:

1. **API Layer** (`src/api/`)
   - FastAPI route handlers
   - Request/response models
   - Route dependencies
   - Input validation

2. **Service Layer** (`src/services/`)
   - Business logic
   - Orchestration between repositories
   - Domain rules enforcement
   - Transaction management

3. **Repository Layer** (`src/repositories/`)
   - Data access abstraction
   - Database queries
   - CRUD operations
   - Query builders

4. **Model Layer** (`src/models/`)
   - SQLAlchemy ORM models
   - Database schema definitions
   - Relationships and constraints

5. **Schema Layer** (`src/schemas/`)
   - Pydantic models for validation
   - Request/response DTOs
   - Data transformation rules

### Design Patterns

- **Repository Pattern**: Abstract data access
- **Service Pattern**: Encapsulate business logic
- **Dependency Injection**: Manage dependencies through FastAPI's DI
- **Factory Pattern**: Generate test data
- **Mapper Pattern**: Transform data between layers
- **Circuit Breaker**: Handle external service failures
- **Retry Pattern**: Automatic retry with exponential backoff

### Data Flow

```
Request → Middleware → Router → Dependency → Service → Repository → Database
                                                    ↓
Response ← Middleware ← Router ← Schema ← Mapper ← Model
```

## 🔒 Security

### Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication
- **Access Tokens**: Short-lived tokens for API access (30 minutes default)
- **Refresh Tokens**: Long-lived tokens for token renewal (7 days default)
- **Password Hashing**: Bcrypt with configurable rounds
- **Token Blacklisting**: Support for token revocation (via Redis)

### Security Features

- **Password Requirements**: Enforced through Pydantic validators
- **Rate Limiting**: Prevent abuse and DDoS attacks
- **CORS**: Configurable cross-origin policies
- **Request ID**: Track and audit requests
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **Input Validation**: Pydantic schema validation
- **Error Messages**: No sensitive information leakage

### Security Best Practices

```python
# Never commit secrets - use environment variables
JWT_SECRET_KEY=your-secret-key-here

# Use strong passwords
# Implement password rotation
# Enable HTTPS in production
# Regular security updates
# Monitor and log security events
```

## 🔧 Extending the Application

### Adding a New Resource

1. **Create Model** (`src/models/`)
```python
from src.db.postgres.mixins import TimestampMixin, PKMixin

class Product(PKMixin, TimestampMixin):
    __tablename__ = "products"
    name = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
```

2. **Create Schemas** (`src/schemas/`)
```python
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float

class ProductResponse(ProductCreate):
    id: int
```

3. **Create Repository** (`src/repositories/`)
```python
from src.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    pass
```

4. **Create Service** (`src/services/`)
```python
from src.services.base import BaseService

class ProductService(BaseService):
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
```

5. **Create API Routes** (`src/api/`)
```python
from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
async def list_products():
    # Implementation
    pass
```

6. **Create Migration**
```bash
make revision
# Enter: "add products table"
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `make test`
5. **Run linter**: `make lint`
6. **Format code**: `make format`
7. **Commit changes**: `git commit -m 'Add amazing feature'`
8. **Push to branch**: `git push origin feature/amazing-feature`
9. **Open a Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for public functions
- Keep functions small and focused
- Write tests for new features

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Support

- **Documentation**: Check the `/docs` directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Redis](https://redis.io/)
- [PostgreSQL](https://www.postgresql.org/)

---

**Happy Coding! 🚀**
