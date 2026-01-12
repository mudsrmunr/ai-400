# ============================================================================
# TASK MODEL (models/task.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   Defines the TASK entity - what a task looks like in our database.
#
# WHAT IS A MODEL?
#   A Python class that represents a database table.
#   - Class = Table definition
#   - Class attributes = Columns
#   - Class instance = One row of data
#
# EXAMPLE:
#   Task class     →  "task" table in database
#   Task(title="Buy milk")  →  One row in that table
#
# HOW SQLMODEL WORKS:
#   1. You define a Python class with type hints
#   2. SQLModel reads those hints
#   3. SQLModel creates the SQL table structure
#   4. You work with Python objects, SQLModel handles SQL
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# SQLModel: Base class for creating database models
# Field: Used to customize column settings (default, nullable, etc.)
from sqlmodel import SQLModel, Field

# Optional: Type hint for fields that can be None
from typing import Optional

# datetime: For date/time fields (created_at, updated_at, due_date)
# timezone: For timezone-aware timestamps (UTC)
from datetime import datetime, timezone

# Enum: For fields with fixed set of allowed values
from enum import Enum


# ----------------------------------------------------------------------------
# ENUMS (Fixed Value Sets)
# ----------------------------------------------------------------------------
#
# WHAT IS AN ENUM?
#   A way to define a fixed set of allowed values.
#   Instead of any string, only specific values are allowed.
#
# WHY USE ENUMS?
#   - Prevents typos ("pending" vs "pendig")
#   - Self-documenting (you can see all valid options)
#   - Type safety (IDE autocomplete works)
#   - Database consistency (no random values)
#

class TaskStatus(str, Enum):
    """
    Allowed status values for a task.

    Inherits from both str and Enum so values are strings
    that can be easily serialized to JSON.

    Values:
        PENDING: Task not started yet
        IN_PROGRESS: Task is being worked on
        COMPLETED: Task is finished
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """
    Allowed priority levels for a task.

    Values:
        LOW: Can wait, not urgent
        MEDIUM: Normal priority
        HIGH: Urgent, do soon
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ----------------------------------------------------------------------------
# TASK MODEL
# ----------------------------------------------------------------------------
#
# WHAT DOES table=True MEAN?
#   - table=True: This class IS a database table (creates actual table)
#   - table=False (default): Just a data structure (no table created)
#
# FIELD BREAKDOWN:
#   - Type hint (str, int, etc.) = Column data type
#   - Optional[X] = Column can be NULL
#   - Field(...) = Extra settings (default, primary key, etc.)
#

class Task(SQLModel, table=True):
    """
    Task model representing a task in the database.

    This class defines:
    1. The structure of the "task" table in the database
    2. Validation rules for task data
    3. Default values for optional fields

    Attributes:
        id: Unique identifier (auto-generated)
        title: Task title (required, max 200 chars)
        description: Detailed description (optional)
        status: Current status (pending/in_progress/completed)
        priority: Priority level (low/medium/high)
        due_date: When task should be completed (optional)
        created_at: When task was created (auto-set)
        updated_at: When task was last modified (auto-set)

    Example:
        task = Task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            priority=TaskPriority.HIGH
        )
    """

    # -------------------------------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------------------------------
    # id: Unique identifier for each task
    #
    # WHAT IS A PRIMARY KEY?
    #   A unique identifier for each row. No two rows can have the same id.
    #   Like a social security number for your data.
    #
    # PARAMETERS:
    #   - default=None: Don't require id when creating (database will generate)
    #   - primary_key=True: This is THE unique identifier
    #
    # TYPE: int | None
    #   - int: It will be an integer
    #   - | None: Can be None when creating (before database assigns id)
    #
    id: int | None = Field(default=None, primary_key=True)

    # -------------------------------------------------------------------------
    # REQUIRED FIELDS
    # -------------------------------------------------------------------------
    # These fields MUST be provided when creating a task.

    # title: The name/title of the task
    # Type: str (required - no Optional, no default)
    # max_length: Maximum characters allowed (prevents huge titles)
    # index=True: Creates database index for faster searching
    title: str = Field(
        ...,  # ... means "required" (no default value)
        max_length=200,
        description="The title of the task"
    )

    # -------------------------------------------------------------------------
    # OPTIONAL FIELDS (with defaults)
    # -------------------------------------------------------------------------
    # These fields have default values, so they're optional when creating.

    # description: Detailed description of the task
    # Type: Optional[str] = can be None
    # Default: None (no description)
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Detailed description of the task"
    )

    # status: Current state of the task
    # Type: TaskStatus (our enum above)
    # Default: PENDING (new tasks start as pending)
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current status of the task"
    )

    # priority: How urgent is this task
    # Type: TaskPriority (our enum above)
    # Default: MEDIUM (normal priority)
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Priority level of the task"
    )

    # due_date: When should this task be completed
    # Type: Optional[datetime] = can be None
    # Default: None (no due date)
    due_date: Optional[datetime] = Field(
        default=None,
        description="When the task should be completed"
    )

    # -------------------------------------------------------------------------
    # TIMESTAMP FIELDS (auto-managed)
    # -------------------------------------------------------------------------
    # These track when records were created and modified.

    # created_at: When was this task created
    # default_factory: Calls a function when creating to get current UTC time
    # This means: automatically set to current time when task is created
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the task was created"
    )

    # updated_at: When was this task last modified
    # Initially same as created_at
    # NOTE: You need to manually update this when modifying tasks
    # (We'll handle this in CRUD operations)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the task was last updated"
    )


# ----------------------------------------------------------------------------
# HOW THIS BECOMES A DATABASE TABLE
# ----------------------------------------------------------------------------
#
# When create_db_and_tables() runs in database.py, SQLModel creates:
#
#   CREATE TABLE task (
#       id INTEGER PRIMARY KEY AUTOINCREMENT,
#       title VARCHAR(200) NOT NULL,
#       description VARCHAR(1000),
#       status VARCHAR(11) DEFAULT 'pending',
#       priority VARCHAR(6) DEFAULT 'medium',
#       due_date DATETIME,
#       created_at DATETIME NOT NULL,
#       updated_at DATETIME NOT NULL
#   );
#
# You write Python, SQLModel writes SQL!
#


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. MODELS:
#    - Python class that represents a database table
#    - table=True makes it a real table
#    - Attributes become columns
#
# 2. FIELD TYPES:
#    - str, int, datetime = column data types
#    - Optional[X] = can be NULL
#    - Field(...) = extra settings
#
# 3. ENUMS:
#    - Fixed set of allowed values
#    - Prevents invalid data
#    - Self-documenting
#
# 4. FIELD OPTIONS:
#    - primary_key=True: unique identifier
#    - default=X: default value if not provided
#    - default_factory=func: call function for default
#    - max_length=N: limit string length
#
# 5. CONVENTIONS:
#    - id as primary key
#    - created_at/updated_at for tracking
#    - Enums for fixed value sets
#
# ============================================================================
