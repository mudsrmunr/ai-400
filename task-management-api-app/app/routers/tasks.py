# ============================================================================
# TASKS ROUTER (routers/tasks.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   Defines all API endpoints for tasks:
#   - POST   /tasks      → Create a new task
#   - GET    /tasks      → Get all tasks
#   - GET    /tasks/{id} → Get one task by ID
#   - PUT    /tasks/{id} → Update a task
#   - DELETE /tasks/{id} → Delete a task
#
# HOW IT WORKS:
#   1. User sends HTTP request (e.g., POST /tasks)
#   2. FastAPI matches to correct function
#   3. Function validates input (using schemas)
#   4. Function calls CRUD operation
#   5. Function returns response
#
# DEPENDENCY INJECTION:
#   FastAPI automatically provides database session to each function.
#   We declare: session: Session = Depends(get_session)
#   FastAPI handles: creating session, passing it, closing it
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# APIRouter: Creates a group of related endpoints
# HTTPException: For returning errors (404, 400, etc.)
# Depends: For dependency injection (automatic session)
# status: HTTP status codes (200, 201, 404, etc.)
from fastapi import APIRouter, HTTPException, Depends, status

# Session: Type hint for database session
from sqlmodel import Session

# List: Type hint for list of items
from typing import List

# Database session provider
from app.database import get_session

# Task model
from app.models.task import Task

# Task schemas (what API accepts/returns)
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskList

# CRUD operations (database functions)
from app.crud.task import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task
)


# ----------------------------------------------------------------------------
# CREATE ROUTER
# ----------------------------------------------------------------------------
#
# APIRouter groups related endpoints together.
#
# Parameters:
#   - prefix: URL prefix for all routes ("/tasks")
#   - tags: Category name in API docs (Swagger UI)
#

router = APIRouter(
    prefix="/tasks",          # All routes start with /tasks
    tags=["Tasks"],           # Shows as "Tasks" section in docs
)


# ----------------------------------------------------------------------------
# CREATE TASK ENDPOINT
# ----------------------------------------------------------------------------
#
# POST /tasks
#
# Creates a new task in the database.
#
# Request body: TaskCreate schema
# Response: TaskRead schema (includes id and timestamps)
# Status code: 201 Created
#

@router.post(
    "/",                              # Path (combined with prefix = /tasks/)
    response_model=TaskRead,          # What the response looks like
    status_code=status.HTTP_201_CREATED,  # 201 = Created successfully
    summary="Create a new task",      # Short description in docs
    description="Create a new task with title and optional fields."
)
def create_new_task(
    task_data: TaskCreate,                      # Request body (validated automatically)
    session: Session = Depends(get_session)     # Database session (injected by FastAPI)
) -> Task:
    """
    Create a new task.

    **Required fields:**
    - **title**: The task title (1-200 characters)

    **Optional fields:**
    - **description**: Detailed description
    - **status**: pending (default), in_progress, or completed
    - **priority**: low, medium (default), or high
    - **due_date**: ISO 8601 datetime format

    **Returns:** The created task with generated id and timestamps.

    **Example request:**
    ```json
    {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": "high"
    }
    ```
    """
    # Call CRUD function to create task
    # CRUD handles all database operations
    return create_task(session=session, task_data=task_data)


# ----------------------------------------------------------------------------
# GET ALL TASKS ENDPOINT
# ----------------------------------------------------------------------------
#
# GET /tasks
#
# Returns a list of all tasks with pagination.
#
# Query parameters:
#   - skip: Number of tasks to skip (default 0)
#   - limit: Maximum tasks to return (default 100)
#

@router.get(
    "/",
    response_model=TaskList,          # Returns list with count
    summary="Get all tasks",
    description="Retrieve a list of all tasks with pagination support."
)
def read_tasks(
    skip: int = 0,                              # Query param: ?skip=10
    limit: int = 100,                           # Query param: ?limit=20
    session: Session = Depends(get_session)
) -> dict:
    """
    Get a list of all tasks.

    **Query parameters:**
    - **skip**: Number of tasks to skip (for pagination)
    - **limit**: Maximum number of tasks to return (max 100)

    **Pagination example:**
    - Page 1: `/tasks?skip=0&limit=10`
    - Page 2: `/tasks?skip=10&limit=10`
    - Page 3: `/tasks?skip=20&limit=10`

    **Returns:** Object with `tasks` array and `count`.
    """
    # Get tasks from database
    tasks = get_tasks(session=session, skip=skip, limit=limit)

    # Return as TaskList schema (tasks + count)
    return {"tasks": tasks, "count": len(tasks)}


# ----------------------------------------------------------------------------
# GET ONE TASK ENDPOINT
# ----------------------------------------------------------------------------
#
# GET /tasks/{task_id}
#
# Returns a single task by its ID.
# Returns 404 if task not found.
#

@router.get(
    "/{task_id}",                     # Path parameter in URL
    response_model=TaskRead,
    summary="Get a task by ID",
    description="Retrieve a single task by its unique identifier."
)
def read_task(
    task_id: int,                               # Path parameter (from URL)
    session: Session = Depends(get_session)
) -> Task:
    """
    Get a single task by ID.

    **Path parameter:**
    - **task_id**: The unique identifier of the task

    **Returns:** The task object if found.

    **Raises:** 404 Not Found if task doesn't exist.

    **Example:** `GET /tasks/1` returns task with id=1.
    """
    # Get task from database
    task = get_task(session=session, task_id=task_id)

    # If task not found, raise 404 error
    # HTTPException stops execution and returns error response
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    return task


# ----------------------------------------------------------------------------
# UPDATE TASK ENDPOINT
# ----------------------------------------------------------------------------
#
# PUT /tasks/{task_id}
#
# Updates an existing task.
# Only updates fields that are provided (partial update supported).
# Returns 404 if task not found.
#

@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Update an existing task. Only provided fields are updated."
)
def update_existing_task(
    task_id: int,                               # From URL path
    task_data: TaskUpdate,                      # From request body
    session: Session = Depends(get_session)
) -> Task:
    """
    Update an existing task.

    **Path parameter:**
    - **task_id**: The unique identifier of the task to update

    **Request body:** TaskUpdate schema (all fields optional)

    Only include fields you want to change.
    Fields not included remain unchanged.

    **Example:** Update only status:
    ```json
    {
        "status": "completed"
    }
    ```

    **Raises:** 404 Not Found if task doesn't exist.
    """
    # Call CRUD function to update
    task = update_task(session=session, task_id=task_id, task_data=task_data)

    # If task not found (CRUD returned None), raise 404
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    return task


# ----------------------------------------------------------------------------
# DELETE TASK ENDPOINT
# ----------------------------------------------------------------------------
#
# DELETE /tasks/{task_id}
#
# Permanently deletes a task.
# Returns 404 if task not found.
# Returns 204 No Content on success (no body).
#

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,    # 204 = Deleted, no content to return
    summary="Delete a task",
    description="Permanently delete a task from the database."
)
def delete_existing_task(
    task_id: int,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a task permanently.

    **Path parameter:**
    - **task_id**: The unique identifier of the task to delete

    **Returns:** Nothing (204 No Content on success)

    **Raises:** 404 Not Found if task doesn't exist.

    **Warning:** This action cannot be undone!
    """
    # Call CRUD function to delete
    success = delete_task(session=session, task_id=task_id)

    # If task not found (CRUD returned False), raise 404
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Return nothing (204 No Content)
    # FastAPI handles this automatically when return type is None


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. ROUTER PATTERN:
#    - APIRouter groups related endpoints
#    - prefix="/tasks" → all routes start with /tasks
#    - tags=["Tasks"] → category in API docs
#
# 2. ENDPOINT DECORATORS:
#    - @router.post("/") → POST /tasks
#    - @router.get("/") → GET /tasks
#    - @router.get("/{id}") → GET /tasks/{id}
#    - @router.put("/{id}") → PUT /tasks/{id}
#    - @router.delete("/{id}") → DELETE /tasks/{id}
#
# 3. DEPENDENCY INJECTION:
#    - session: Session = Depends(get_session)
#    - FastAPI automatically creates and closes session
#
# 4. RESPONSE MODELS:
#    - response_model=TaskRead → validates output
#    - FastAPI automatically converts to JSON
#
# 5. ERROR HANDLING:
#    - HTTPException raises HTTP errors
#    - status.HTTP_404_NOT_FOUND = 404
#    - detail= message shown to user
#
# 6. STATUS CODES:
#    - 200 OK (default for GET)
#    - 201 Created (POST success)
#    - 204 No Content (DELETE success)
#    - 404 Not Found (doesn't exist)
#
# ============================================================================
