# ============================================================================
# TEST CONFIGURATION (conftest.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   Contains "fixtures" - reusable setup code for tests.
#   pytest automatically finds and uses this file.
#
# WHAT ARE FIXTURES?
#   Functions that provide data or setup for tests.
#   They run before each test that needs them.
#
# WHY USE FIXTURES?
#   - Avoid repeating setup code in every test
#   - Ensure tests are isolated (fresh database each time)
#   - Make tests cleaner and more readable
#
# IMPORTANT:
#   Tests use an IN-MEMORY SQLite database.
#   This means:
#   - Super fast (no disk writes)
#   - Fresh database for each test
#   - Doesn't affect your real database
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# pytest: Testing framework
import pytest

# FastAPI testing tools
from fastapi.testclient import TestClient

# SQLModel database tools
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Our application
from app.main import app

# Database session dependency (we'll override this)
from app.database import get_session


# ----------------------------------------------------------------------------
# TEST DATABASE SETUP
# ----------------------------------------------------------------------------
#
# We create a SEPARATE database for testing.
# This is an IN-MEMORY SQLite database:
#   - Lives only in RAM (no file created)
#   - Super fast
#   - Destroyed when tests finish
#   - Doesn't interfere with real data
#

# Connection string for in-memory SQLite
# "sqlite://" without a file path = in-memory database
TEST_DATABASE_URL = "sqlite://"


# ----------------------------------------------------------------------------
# DATABASE FIXTURES
# ----------------------------------------------------------------------------

@pytest.fixture(name="engine")
def engine_fixture():
    """
    Create a test database engine.

    Uses in-memory SQLite with StaticPool.
    StaticPool ensures the same connection is reused
    (required for in-memory SQLite to persist data during test).

    Yields:
        Engine: SQLAlchemy engine for test database
    """
    # Create engine with special settings for testing
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},  # Allow multi-thread access
        poolclass=StaticPool,  # Keep single connection alive
    )

    # Create all tables in test database
    SQLModel.metadata.create_all(engine)

    # Provide engine to tests
    yield engine

    # Cleanup: Drop all tables after tests
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """
    Create a database session for tests.

    This session is connected to the test database (in-memory).
    Each test gets a fresh session.

    Args:
        engine: The test database engine (from engine_fixture)

    Yields:
        Session: Database session for test operations
    """
    # Create session connected to test engine
    with Session(engine) as session:
        yield session


# ----------------------------------------------------------------------------
# CLIENT FIXTURE
# ----------------------------------------------------------------------------

@pytest.fixture(name="client")
def client_fixture(session):
    """
    Create a test client for making HTTP requests to the API.

    This client:
    - Makes requests to our FastAPI app
    - Uses the test database (not real database)
    - Behaves like a real HTTP client

    Args:
        session: Test database session (from session_fixture)

    Yields:
        TestClient: Client for making test requests

    How it works:
        1. Override the get_session dependency
        2. Make it return our test session instead
        3. All API requests now use test database
    """
    # Function to override get_session dependency
    def get_session_override():
        return session

    # Replace real get_session with test version
    app.dependency_overrides[get_session] = get_session_override

    # Create test client
    client = TestClient(app)

    # Provide client to tests
    yield client

    # Cleanup: Remove the override
    app.dependency_overrides.clear()


# ----------------------------------------------------------------------------
# HELPER FIXTURES
# ----------------------------------------------------------------------------

@pytest.fixture(name="sample_task")
def sample_task_fixture(client):
    """
    Create a sample task for tests that need existing data.

    This fixture:
    1. Creates a task via the API
    2. Returns the created task data
    3. Task is automatically cleaned up (in-memory DB)

    Args:
        client: Test client (from client_fixture)

    Returns:
        dict: The created task data including id
    """
    # Create a sample task
    task_data = {
        "title": "Test Task",
        "description": "A task for testing",
        "status": "pending",
        "priority": "medium"
    }

    # Make POST request to create task
    response = client.post("/tasks/", json=task_data)

    # Return the created task (includes id)
    return response.json()


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. FIXTURES:
#    - @pytest.fixture decorator creates reusable setup
#    - name="x" lets you use different name in tests
#    - yield provides value, code after yield = cleanup
#
# 2. TEST DATABASE:
#    - In-memory SQLite (sqlite://)
#    - StaticPool keeps connection alive
#    - Fresh database for each test
#
# 3. DEPENDENCY OVERRIDE:
#    - app.dependency_overrides[func] = replacement
#    - Makes API use test database
#    - Critical for isolated testing
#
# 4. TEST CLIENT:
#    - TestClient simulates HTTP requests
#    - client.get(), client.post(), etc.
#    - Returns Response objects
#
# ============================================================================
