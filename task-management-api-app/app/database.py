# ============================================================================
# DATABASE CONNECTION MODULE (database.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   The "key" to your database. Handles all connection logic.
#
# WHAT DOES IT DO?
#   1. Creates an ENGINE (connection configuration)
#   2. Provides SESSIONS (conversations with database)
#   3. Creates TABLES when app starts
#
# ANALOGY:
#   - Engine = Key to your storage locker
#   - Session = One trip to the locker (open, do stuff, close)
#   - Tables = Shelves inside the locker
#
# WHY SEPARATE FILE?
#   - Single place for all database logic
#   - Easy to change database settings
#   - Other files import from here
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# SQLModel: Our ORM library (combines SQLAlchemy + Pydantic)
# - create_engine: Creates the database connection
# - Session: Manages conversations with database
# - SQLModel: Base class for our models
from sqlmodel import create_engine, Session, SQLModel

# contextmanager: Helps create "with" blocks for safe resource handling
# Example: with get_session() as session: ...
from contextlib import contextmanager

# Generator: Type hint for functions that yield values
from typing import Generator

# Import our settings (database URL, debug mode, etc.)
from app.config import settings


# ----------------------------------------------------------------------------
# DATABASE ENGINE
# ----------------------------------------------------------------------------
#
# WHAT IS AN ENGINE?
#   The Engine is the starting point for any SQLAlchemy/SQLModel application.
#   It holds the connection URL and configuration.
#
# WHAT IS A CONNECTION URL?
#   A string that tells SQLModel WHERE and HOW to connect:
#
#   SQLite (local file):
#   sqlite:///./task_management.db
#   │         │
#   │         └── File path
#   └── Database type
#
#   PostgreSQL (Neon):
#   postgresql://user:pass@host/dbname
#   │            │    │    │    │
#   │            │    │    │    └── Database name
#   │            │    │    └── Server address
#   │            │    └── Password
#   │            └── Username
#   └── Database type
#
# IMPORTANT PARAMETERS:
#   - echo: If True, prints all SQL commands (helpful for debugging)
#   - connect_args: Extra connection settings
#

# Check if we're using SQLite (needed for special settings)
# SQLite requires "check_same_thread": False for FastAPI
# (FastAPI uses multiple threads, SQLite by default allows only one)
is_sqlite = settings.database_url.startswith("sqlite")

# Create connection arguments based on database type
# SQLite needs special handling for multi-threaded apps
connect_args = {"check_same_thread": False} if is_sqlite else {}

# Create the database engine
# This doesn't connect yet - it just holds the configuration
engine = create_engine(
    # The database URL from our settings (.env file)
    settings.database_url,

    # echo=True prints SQL commands to console (great for learning!)
    # We enable this in debug mode, disable in production
    echo=settings.debug,

    # Extra connection arguments (SQLite thread safety)
    connect_args=connect_args
)


# ----------------------------------------------------------------------------
# SESSION MANAGEMENT
# ----------------------------------------------------------------------------
#
# WHAT IS A SESSION?
#   A Session is a "conversation" with the database.
#   You open it, do your work (read/write), then close it.
#
# WHY DO WE NEED SESSIONS?
#   1. Groups related operations together (transaction)
#   2. Tracks changes you've made
#   3. Handles committing (saving) or rolling back (undoing)
#   4. Properly releases database connections when done
#
# ANALOGY:
#   Session is like a shopping trip:
#   1. Enter store (open session)
#   2. Pick items, put in cart (make changes)
#   3. Pay at checkout (commit - save changes)
#   4. Leave store (close session)
#
#   If your card declines (error), you put everything back (rollback)
#


def get_session() -> Generator[Session, None, None]:
    """
    Create a database session for use in API endpoints.

    This is a GENERATOR function (uses 'yield' instead of 'return').
    FastAPI uses this pattern for "dependency injection".

    HOW IT WORKS:
        1. Create a new Session
        2. Give it to the caller (yield)
        3. Caller does their database work
        4. Session automatically closes when done

    USAGE IN ROUTERS (later):
        @router.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            # session is ready to use here
            tasks = session.exec(select(Task)).all()
            return tasks

    Yields:
        Session: A database session for executing queries

    Technical Terms:
        - Generator: Function that yields values one at a time
        - Dependency Injection: FastAPI automatically provides the session
        - Context Manager: Ensures cleanup happens (session closes)
    """
    # Create a new session using our engine
    # "with" ensures the session closes even if an error occurs
    with Session(engine) as session:
        # yield = "pause here and give this session to the caller"
        # When caller is done, execution continues (session closes)
        yield session


@contextmanager
def get_session_context():
    """
    Alternative session getter for use OUTSIDE of FastAPI routes.

    Use this when you need a session in:
    - Startup scripts
    - Background tasks
    - Testing
    - Manual database operations

    USAGE:
        with get_session_context() as session:
            task = Task(title="My Task")
            session.add(task)
            session.commit()

    This is a CONTEXT MANAGER (the @contextmanager decorator).
    It allows using 'with' statement for safe resource handling.

    Yields:
        Session: A database session
    """
    # Create session
    session = Session(engine)
    try:
        # Give session to the caller
        yield session
    finally:
        # ALWAYS close the session, even if an error occurred
        # This prevents "connection leak" (connections staying open forever)
        session.close()


# ----------------------------------------------------------------------------
# TABLE CREATION
# ----------------------------------------------------------------------------
#
# WHAT DOES THIS DO?
#   Creates all database tables based on our SQLModel models.
#
# WHEN IS IT CALLED?
#   At application startup (in main.py)
#
# HOW DOES IT WORK?
#   1. SQLModel looks at all classes that inherit from SQLModel
#   2. For each class marked as table=True, it creates a table
#   3. If table already exists, it does nothing (safe to call multiple times)
#
# IMPORTANT:
#   This is a simple approach for development.
#   For production, you'd use "migrations" (Alembic) to manage schema changes.
#

def create_db_and_tables():
    """
    Create all database tables.

    Call this function once at application startup.
    It creates tables for all SQLModel models that have table=True.

    Safe to call multiple times - existing tables won't be modified.

    WHAT HAPPENS:
        1. SQLModel.metadata collects all model definitions
        2. create_all() generates CREATE TABLE SQL commands
        3. Engine executes the commands on the database
        4. Tables are created (if they don't exist)

    Example:
        # In main.py
        @app.on_event("startup")
        def on_startup():
            create_db_and_tables()
    """
    # SQLModel.metadata.create_all(engine) does the magic:
    # - metadata = collection of all table definitions
    # - create_all = generate and execute CREATE TABLE statements
    # - engine = where to create the tables
    SQLModel.metadata.create_all(engine)


# ----------------------------------------------------------------------------
# OPTIONAL: Health Check Function
# ----------------------------------------------------------------------------
#
# WHY HAVE THIS?
#   To verify database connection is working.
#   Useful for monitoring and debugging.
#

def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection successful, False otherwise

    Usage:
        if check_database_connection():
            print("Database is connected!")
        else:
            print("Database connection failed!")
    """
    try:
        # Try to create a session and execute a simple query
        with Session(engine) as session:
            # Execute a simple query (SELECT 1)
            # If this works, database is connected
            session.exec("SELECT 1")
        return True
    except Exception as e:
        # If any error occurs, connection failed
        # In production, you'd log this error
        print(f"Database connection failed: {e}")
        return False


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. ENGINE:
#    - Holds database connection configuration
#    - Created once, used throughout the app
#    - Reads URL from settings (which reads from .env)
#
# 2. SESSION:
#    - A "conversation" with the database
#    - Open → Do work → Close
#    - Always close sessions to prevent connection leaks
#
# 3. GENERATOR PATTERN:
#    - Functions that yield values
#    - FastAPI uses this for dependency injection
#    - Ensures proper cleanup (session closing)
#
# 4. TABLE CREATION:
#    - create_db_and_tables() creates all tables
#    - Called once at startup
#    - Safe to call multiple times
#
# 5. SECURITY:
#    - Database URL comes from .env (not hardcoded)
#    - SQLite needs special thread settings for FastAPI
#    - echo=debug only shows SQL in development
#
# ============================================================================
