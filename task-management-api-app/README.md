# Task Management API

A Task Management API built with FastAPI, SQLModel, and pytest.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL database interactions with Python type hints
- **pytest**: Testing framework
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL/Neon for production)

## Features

- Create, Read, Update, Delete (CRUD) operations for tasks
- Task properties: title, description, status, priority, due date
- Automatic API documentation (Swagger UI)
- Input validation with Pydantic
- Comprehensive test coverage

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Create `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Open API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
pytest
```

## Project Structure

```
task-management-api/
├── app/
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database connection
│   ├── models/          # SQLModel models
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # API endpoints
│   └── crud/            # Database operations
├── tests/               # Test files
├── .env.example         # Environment variables template
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## License

MIT
