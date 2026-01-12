# ============================================================================
# TASK SCHEMAS (schemas/task.py)
# ============================================================================
#
# WHAT ARE SCHEMAS?
#   Schemas define the SHAPE of data for API requests and responses.
#   They validate incoming data and document what your API expects.
#
# WHY DIFFERENT FROM MODELS?
#   - Model = How data is STORED in database (all fields)
#   - Schema = How data is SENT/RECEIVED via API (operation-specific fields)
#
# EXAMPLE:
#   When creating a task:
#     - User sends: title, description
#     - They DON'T send: id (auto-generated), created_at (auto-set)
#
#   Schema ensures:
#     - Required fields are present
#     - Data types are correct
#     - Invalid data is rejected with clear error messages
#
# NAMING CONVENTION:
#   - TaskCreate = for creating new tasks
#   - TaskUpdate = for updating existing tasks
#   - TaskRead = for returning tasks to users
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# SQLModel: We use SQLModel for schemas too (it's built on Pydantic)
# Field: For setting validation rules
from sqlmodel import SQLModel, Field

# Optional: For fields that can be None
from typing import Optional, List

# datetime: For date/time fields
from datetime import datetime

# Import our enums from the model (reuse them!)
from app.models.task import TaskStatus, TaskPriority


# ----------------------------------------------------------------------------
# BASE SCHEMA
# ----------------------------------------------------------------------------
#
# WHAT IS A BASE SCHEMA?
#   A schema with fields common to multiple operations.
#   Other schemas inherit from it to avoid repetition.
#
# DRY PRINCIPLE:
#   "Don't Repeat Yourself"
#   Define common fields once, reuse everywhere.
#

class TaskBase(SQLModel):
    """
    Base schema with fields common to create and update operations.

    NOT used directly - other schemas inherit from this.

    Why inherit?
        - Avoids repeating the same field definitions
        - Changes in one place apply everywhere
        - Consistent validation across operations
    """
    # title: Required for create, optional for update
    # We'll handle this difference in child schemas
    title: str = Field(
        ...,
        min_length=1,      # At least 1 character
        max_length=200,    # Maximum 200 characters
        description="The title of the task"
    )

    # description: Always optional
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Detailed description of the task"
    )

    # status: Optional with default
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current status (pending, in_progress, completed)"
    )

    # priority: Optional with default
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Priority level (low, medium, high)"
    )

    # due_date: Optional
    due_date: Optional[datetime] = Field(
        default=None,
        description="When the task should be completed (ISO 8601 format)"
    )


# ----------------------------------------------------------------------------
# CREATE SCHEMA
# ----------------------------------------------------------------------------
#
# USED WHEN: User sends POST /tasks to create a new task
#
# WHAT IT VALIDATES:
#   - title is required (inherited from TaskBase)
#   - Other fields are optional with defaults
#   - id, created_at, updated_at are NOT included (auto-generated)
#

class TaskCreate(TaskBase):
    """
    Schema for creating a new task.

    Used with: POST /tasks

    Required fields:
        - title: Must provide a task title

    Optional fields (have defaults):
        - description: Defaults to None
        - status: Defaults to "pending"
        - priority: Defaults to "medium"
        - due_date: Defaults to None

    NOT included (auto-generated):
        - id
        - created_at
        - updated_at

    Example request body:
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high"
        }
    """
    # Inherits all fields from TaskBase
    # No additional fields needed for create
    pass


# ----------------------------------------------------------------------------
# UPDATE SCHEMA
# ----------------------------------------------------------------------------
#
# USED WHEN: User sends PUT/PATCH /tasks/{id} to update a task
#
# IMPORTANT: All fields are OPTIONAL!
#   - User only sends fields they want to change
#   - Fields not sent remain unchanged
#
# EXAMPLE:
#   PUT /tasks/1 with {"status": "completed"}
#   Only updates status, keeps everything else the same
#

class TaskUpdate(SQLModel):
    """
    Schema for updating an existing task.

    Used with: PUT /tasks/{id} or PATCH /tasks/{id}

    ALL fields are optional!
    Only include fields you want to change.

    Example request body (update only status):
        {
            "status": "completed"
        }

    Example request body (update multiple fields):
        {
            "title": "New title",
            "priority": "high",
            "due_date": "2024-12-31T23:59:59"
        }
    """
    # ALL fields are Optional for updates
    # None means "don't change this field"

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New title for the task"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="New description for the task"
    )

    status: Optional[TaskStatus] = Field(
        default=None,
        description="New status (pending, in_progress, completed)"
    )

    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New priority (low, medium, high)"
    )

    due_date: Optional[datetime] = Field(
        default=None,
        description="New due date (ISO 8601 format)"
    )


# ----------------------------------------------------------------------------
# READ SCHEMA
# ----------------------------------------------------------------------------
#
# USED WHEN: API returns task data to the user
#
# INCLUDES: All fields, including id and timestamps
#   - User needs to see the id to reference the task later
#   - Timestamps show when task was created/modified
#

class TaskRead(TaskBase):
    """
    Schema for returning task data in API responses.

    Used with: GET /tasks, GET /tasks/{id}, POST /tasks response

    Includes all fields:
        - id: The unique identifier
        - title, description, status, priority, due_date (from TaskBase)
        - created_at: When task was created
        - updated_at: When task was last modified

    Example response:
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "status": "pending",
            "priority": "high",
            "due_date": null,
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
    """
    # id: Included in responses so user can reference this task
    id: int

    # Timestamps: Show when created and last modified
    created_at: datetime
    updated_at: datetime


# ----------------------------------------------------------------------------
# LIST SCHEMA
# ----------------------------------------------------------------------------
#
# USED WHEN: API returns a list of tasks with metadata
#
# WHY NOT JUST List[TaskRead]?
#   - Sometimes you want pagination info (total count, page number)
#   - Wrapping in a schema allows adding metadata
#

class TaskList(SQLModel):
    """
    Schema for returning a list of tasks with metadata.

    Used with: GET /tasks (list all tasks)

    Includes:
        - tasks: List of task objects
        - count: Total number of tasks returned

    Example response:
        {
            "tasks": [
                {"id": 1, "title": "Task 1", ...},
                {"id": 2, "title": "Task 2", ...}
            ],
            "count": 2
        }
    """
    tasks: List[TaskRead]
    count: int = Field(description="Number of tasks in the list")


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. SCHEMAS vs MODELS:
#    - Model = Database structure (all fields)
#    - Schema = API contract (operation-specific fields)
#
# 2. DIFFERENT SCHEMAS FOR DIFFERENT OPERATIONS:
#    - TaskCreate: Fields needed to create (no id, no timestamps)
#    - TaskUpdate: All fields optional (update only what you send)
#    - TaskRead: All fields including id, timestamps (what API returns)
#
# 3. INHERITANCE:
#    - TaskBase contains common fields
#    - Other schemas inherit to avoid repetition
#    - DRY principle: Don't Repeat Yourself
#
# 4. VALIDATION:
#    - min_length, max_length: String length limits
#    - Field(...): Required field (no default)
#    - Optional[X]: Can be None
#
# 5. WHY THIS MATTERS:
#    - Security: Prevents users from setting id or timestamps
#    - Flexibility: Different rules for different operations
#    - Documentation: FastAPI generates docs from schemas
#
# ============================================================================
