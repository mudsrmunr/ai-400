# ============================================================================
# CONFIGURATION MODULE (config.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   The "control panel" for your entire application.
#   All settings are managed here in ONE place.
#
# WHY DO WE NEED THIS?
#   - Keeps secrets (passwords) OUT of your code
#   - One place to change settings (not scattered everywhere)
#   - Different settings for development vs production
#   - Type checking ensures correct values
#
# HOW DOES IT WORK?
#   1. You put settings in .env file (e.g., DATABASE_URL=...)
#   2. This file reads those settings automatically
#   3. Other files import settings: from app.config import settings
#   4. Use like: settings.database_url
#
# SECURITY:
#   - This file contains NO secrets (safe to upload to GitHub)
#   - All secrets come from .env file (which is in .gitignore)
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# BaseSettings: A special class that reads environment variables automatically
# SettingsConfigDict: Configuration for how to read the .env file
from pydantic_settings import BaseSettings, SettingsConfigDict

# Optional: Used when a value might or might not exist
# Example: test_database_url might not be set
from typing import Optional


# ----------------------------------------------------------------------------
# SETTINGS CLASS
# ----------------------------------------------------------------------------
# Think of this class as a FORM with fields.
# Each field = one setting for your app.
# pydantic-settings automatically fills in values from environment variables.
#
# HOW THE MAGIC WORKS:
#   Field name in class  →  Environment variable name
#   database_url         →  DATABASE_URL
#   debug                →  DEBUG
#   (lowercase)          →  (UPPERCASE)
#

class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings are read from environment variables.
    If not found, default values are used.

    Example:
        from app.config import settings
        print(settings.app_name)  # "Task Management API"
    """

    # =========================================================================
    # APPLICATION SETTINGS (General info about your app)
    # =========================================================================

    # app_name: The name shown in API documentation (Swagger UI)
    # Type: str (text)
    # Default: "Task Management API"
    # Where you'll see it: http://localhost:8000/docs (top of page)
    app_name: str = "Task Management API"

    # app_version: Version number of your API
    # Type: str (text)
    # Default: "1.0.0"
    # Why useful: Track which version is running/deployed
    app_version: str = "1.0.0"

    # environment: Which mode is the app running in?
    # Type: str (text)
    # Default: "development"
    # Options: "development", "testing", "production"
    # Why useful: Different behavior based on environment
    environment: str = "development"

    # debug: Should the app show detailed error messages?
    # Type: bool (True or False)
    # Default: False (safe default)
    #
    # SECURITY WARNING:
    #   - debug=True  → Shows full error details (good for finding bugs)
    #   - debug=False → Hides internal details (safe for production)
    #   - NEVER use debug=True in production! Hackers can learn about your system.
    #
    debug: bool = False


    # =========================================================================
    # DATABASE SETTINGS (How to connect to your database)
    # =========================================================================

    # database_url: The address of your database
    # Type: str (text)
    # Default: SQLite file in current folder
    #
    # WHAT'S IN A DATABASE URL?
    #
    #   For SQLite (local file):
    #   sqlite:///./task_management.db
    #   │       │  │
    #   │       │  └── Database filename
    #   │       └── ./ means "current folder"
    #   └── Database type
    #
    #   For PostgreSQL (Neon - production):
    #   postgresql://username:password@host.neon.tech/dbname?sslmode=require
    #   │            │        │        │              │      │
    #   │            │        │        │              │      └── Use encryption
    #   │            │        │        │              └── Database name
    #   │            │        │        └── Server address
    #   │            │        └── Your password (SECRET!)
    #   │            └── Your username
    #   └── Database type
    #
    # SECURITY: When using Neon, put the URL in .env, NOT here!
    #
    database_url: str = "sqlite:///./task_management.db"

    # test_database_url: Separate database for running tests
    # Type: Optional[str] (text or nothing)
    # Default: None (will create in-memory database for tests)
    #
    # WHY A SEPARATE TEST DATABASE?
    #   - Tests create/delete data constantly
    #   - You don't want test data mixed with real data
    #   - In-memory = super fast (no disk writes)
    #
    test_database_url: Optional[str] = None


    # =========================================================================
    # PYDANTIC SETTINGS CONFIGURATION
    # =========================================================================
    # This tells pydantic-settings HOW to read settings.
    #
    # model_config is like "instructions" for the Settings class.
    #
    model_config = SettingsConfigDict(
        # env_file: Which file contains environment variables?
        # ".env" = Look for file named .env in project root
        env_file=".env",

        # env_file_encoding: How is the file encoded?
        # "utf-8" = Standard encoding (supports all characters)
        env_file_encoding="utf-8",

        # case_sensitive: Does capitalization matter?
        # False = DATABASE_URL and database_url are the same
        case_sensitive=False,

        # extra: What to do with unknown variables in .env?
        # "ignore" = Don't crash if there are extra variables
        extra="ignore"
    )


# ----------------------------------------------------------------------------
# CREATE SETTINGS INSTANCE
# ----------------------------------------------------------------------------
# We create ONE settings object that the whole app shares.
# This is called "Singleton Pattern" - only one instance exists.
#
# When this line runs:
#   1. Python finds .env file
#   2. Reads all variables from it
#   3. Matches them to our Settings fields
#   4. Validates the types
#   5. Creates the settings object
#
# HOW TO USE IN OTHER FILES:
#   from app.config import settings
#   print(settings.database_url)
#   print(settings.debug)
#
settings = Settings()


# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------
# These functions make it easy to check which environment we're in.
# Instead of writing: settings.environment == "production"
# You can write: is_production()
#

def is_production() -> bool:
    """
    Check if running in production environment.

    Returns:
        True if environment is "production", False otherwise

    Example:
        if is_production():
            # Use strict security settings
            pass
    """
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """
    Check if running in development environment.

    Returns:
        True if environment is "development", False otherwise

    Example:
        if is_development():
            # Enable debug features
            pass
    """
    return settings.environment.lower() == "development"


def is_testing() -> bool:
    """
    Check if running in testing environment.

    Returns:
        True if environment is "testing", False otherwise

    Example:
        if is_testing():
            # Use test database
            pass
    """
    return settings.environment.lower() == "testing"


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. CONFIGURATION PATTERN:
#    - All settings in one place
#    - Read from environment variables
#    - Safe defaults for development
#
# 2. SECURITY PRACTICES:
#    - Secrets in .env file (not in code)
#    - debug=False in production
#    - Different databases for dev/test/prod
#
# 3. PYTHON CONCEPTS:
#    - Classes (Settings is a class)
#    - Type hints (str, bool, Optional[str])
#    - Default values (= "value")
#    - Docstrings ("""...""" explanations)
#
# 4. PYDANTIC-SETTINGS:
#    - Automatic environment variable reading
#    - Type validation
#    - .env file support
#
# ============================================================================
