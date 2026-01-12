# ============================================================================
# APPLICATION ENTRY POINT (main.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   The main entry point for the FastAPI application.
#   This is where everything comes together.
#
# WHAT DOES IT DO?
#   1. Creates the FastAPI application instance
#   2. Registers all routers (endpoints)
#   3. Sets up startup events (database tables)
#   4. Provides a health check endpoint
#
# HOW TO RUN:
#   uvicorn app.main:app --reload
#
#   Breaking this down:
#   - app.main = the module (app/main.py)
#   - :app = the variable name of FastAPI instance
#   - --reload = restart on code changes (development only)
#
# WHAT YOU'LL SEE:
#   - API docs: http://localhost:8000/docs
#   - Alternative docs: http://localhost:8000/redoc
#   - Health check: http://localhost:8000/
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# FastAPI: The web framework
from fastapi import FastAPI

# contextmanager: For lifespan events (startup/shutdown)
from contextlib import asynccontextmanager

# Our configuration (app name, version, debug)
from app.config import settings

# Database setup (create tables function)
from app.database import create_db_and_tables

# Our task router (all /tasks endpoints)
from app.routers import tasks_router


# ----------------------------------------------------------------------------
# LIFESPAN CONTEXT MANAGER
# ----------------------------------------------------------------------------
#
# WHAT IS LIFESPAN?
#   Code that runs when the app starts and when it shuts down.
#
# WHY USE IT?
#   - Create database tables on startup
#   - Clean up resources on shutdown
#   - Initialize connections, caches, etc.
#
# HOW IT WORKS:
#   1. App starts → code BEFORE yield runs (startup)
#   2. App runs and serves requests
#   3. App shuts down → code AFTER yield runs (shutdown)
#

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    This function runs:
    - BEFORE yield: When the app starts (startup events)
    - AFTER yield: When the app shuts down (shutdown events)

    Startup tasks:
    - Create database tables if they don't exist

    Shutdown tasks:
    - (None currently, but you could close connections, etc.)
    """
    # -------------------------
    # STARTUP EVENTS
    # -------------------------
    # This code runs ONCE when the server starts

    print("[STARTUP] Starting up...")

    # Create database tables
    # This is safe to call multiple times - only creates if not exists
    print("[STARTUP] Creating database tables...")
    create_db_and_tables()
    print("[STARTUP] Database tables ready!")

    # yield = "pause here, let the app run"
    # Everything after this runs on shutdown
    yield

    # -------------------------
    # SHUTDOWN EVENTS
    # -------------------------
    # This code runs ONCE when the server shuts down

    print("[SHUTDOWN] Shutting down...")
    # Add cleanup code here if needed
    # Examples: close database connections, flush caches, etc.


# ----------------------------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ----------------------------------------------------------------------------
#
# This is THE main application object.
# All configuration, routes, and middleware are attached to this.
#

app = FastAPI(
    # Basic information (shown in API docs)
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Task Management API

A RESTful API for managing tasks with full CRUD operations.

### Features:
- Create, read, update, and delete tasks
- Task properties: title, description, status, priority, due date
- Automatic timestamps (created_at, updated_at)
- Input validation
- Pagination support

### Tech Stack:
- **FastAPI**: Modern web framework
- **SQLModel**: Database ORM
- **SQLite/PostgreSQL**: Database
    """,

    # Lifespan handler (startup/shutdown events)
    lifespan=lifespan,

    # API docs configuration
    docs_url="/docs",           # Swagger UI URL
    redoc_url="/redoc",         # ReDoc URL

    # Debug mode from settings
    debug=settings.debug,
)


# ----------------------------------------------------------------------------
# REGISTER ROUTERS
# ----------------------------------------------------------------------------
#
# Routers contain groups of endpoints.
# We "include" them in the main app to activate them.
#
# After this, all /tasks/* endpoints are available.
#

app.include_router(tasks_router)


# ----------------------------------------------------------------------------
# ROOT ENDPOINT (Health Check)
# ----------------------------------------------------------------------------
#
# GET /
#
# A simple endpoint to check if the API is running.
# Useful for monitoring and load balancers.
#

@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running."
)
def root():
    """
    Root endpoint - Health check.

    Returns basic information about the API.
    Use this to verify the API is running.

    **Example response:**
    ```json
    {
        "message": "Welcome to Task Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }
    ```
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "healthy"
    }


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. FASTAPI APPLICATION:
#    - FastAPI() creates the main application
#    - title, version, description shown in docs
#    - debug mode from settings
#
# 2. LIFESPAN EVENTS:
#    - @asynccontextmanager for startup/shutdown
#    - Code before yield = startup
#    - Code after yield = shutdown
#
# 3. ROUTER REGISTRATION:
#    - app.include_router(router) activates endpoints
#    - Routers can have prefixes (/tasks)
#
# 4. RUNNING THE APP:
#    - uvicorn app.main:app --reload
#    - app.main = module path
#    - :app = variable name
#    - --reload = auto-restart on changes
#
# 5. API DOCS:
#    - /docs = Swagger UI (interactive)
#    - /redoc = ReDoc (prettier)
#
# ============================================================================
