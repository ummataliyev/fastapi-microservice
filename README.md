### Getting Started

1. **Clone the repository:**
   ```bash
.   ```

2. **Set up environment variables:**
   - Create a `.env` file in the project's root directory.
   ```bash
   cp .env-example .env
   ```


3. **Build and run the application:**
   ```bash
   make up
   ```

4. **Usage:**
    - All common Docker and project tasks can be run using `make`:

    ##### `make up` - Build and start all services 
    ##### `make down` - Stop all services 
    ##### `make restart` - Restart API container 
    ##### `make logs` - Show logs 
    ##### `make shell` - Open a bash shell inside the API container 
    ##### `make psql` - Connect to PostgreSQL database 
    ##### `make clean`- Remove all containers and volumes (clean start) 
    ##### `make build` - Build Docker images 
    ##### `make upgrade` - Apply all database migrations 
    ##### `make revision` - Create a new migration (prompts for comment) 
    ##### `make test` - Run tests 
    ##### `make lint` - Run code linting 
    ##### `make format` - Auto-format and fix code issues 

5. **Access the application:**
    - API documentation is available at:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
