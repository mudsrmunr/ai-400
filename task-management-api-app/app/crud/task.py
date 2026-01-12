# ============================================================================
# TASK CRUD OPERATIONS (crud/task.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   Contains all database operations for tasks:
#   - CREATE: Add new tasks
#   - READ: Get one task or list of tasks
#   - UPDATE: Modify existing tasks
#   - DELETE: Remove tasks
#
# WHY SEPARATE FROM ROUTERS?
#   - Routers handle HTTP (requests/responses)
#   - CRUD handles DATABASE (storing/retrieving)
#   - Separation of concerns = cleaner code
#   - CRUD can be reused (routes, scripts, tests)
#
# HOW IT WORKS:
#   1. Router receives request
#   2. Router calls CRUD function
#   3. CRUD function talks to database
#   4. CRUD returns result to router
#   5. Router sends response to user
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# Session: For database conversations
from sqlmodel import Session, select

# Optional, List: Type hints
from typing import Optional, List

# datetime: For updating timestamps
# timezone: For timezone-aware timestamps (UTC)
from datetime import datetime, timezone

# Our Task model (database table structure)
from app.models.task import Task

# Our schemas (what data looks like for each operation)
from app.schemas.task import TaskCreate, TaskUpdate


# ----------------------------------------------------------------------------
# CREATE OPERATION
# ----------------------------------------------------------------------------
#
# WHAT IT DOES:
#   Takes task data from user and saves it to database.
#
# STEPS:
#   1. Receive TaskCreate schema (validated input)
#   2. Create Task model instance
#   3. Add to database session
#   4. Commit (save) to database
#   5. Refresh (get auto-generated fields like id)
#   6. Return the created task
#

def create_task(session: Session, task_data: TaskCreate) -> Task:
    """
    Create a new task in the database.

    Args:
        session: Database session (connection)
        task_data: TaskCreate schema with task information

    Returns:
        Task: The newly created task with id and timestamps

    Example:
        task_input = TaskCreate(title="Buy groceries", priority="high")
        new_task = create_task(session, task_input)
        print(new_task.id)  # Auto-generated ID

    What happens:
        1. task_data.model_dump() converts schema to dictionary
        2. Task(**dict) creates model instance from dictionary
        3. session.add() marks task for insertion
        4. session.commit() saves to database
        5. session.refresh() updates object with DB-generated values
    """
    # Convert schema to dictionary, then create Task model
    # model_dump() is Pydantic's way to convert to dict
    task = Task(**task_data.model_dump())

    # Add task to session (mark for insertion)
    # This doesn't save yet - just tells session "I want to add this"
    session.add(task)

    # Commit the transaction (actually save to database)
    # If this fails, changes are rolled back
    session.commit()

    # Refresh the task object with database-generated values
    # This gets the auto-generated id, created_at, etc.
    session.refresh(task)

    # Return the complete task with all fields
    return task


# ----------------------------------------------------------------------------
# READ OPERATIONS
# ----------------------------------------------------------------------------
#
# Two types of read:
#   1. Get ONE task by ID
#   2. Get ALL tasks (with optional filters)
#

def get_task(session: Session, task_id: int) -> Optional[Task]:
    """
    Get a single task by its ID.

    Args:
        session: Database session
        task_id: The unique identifier of the task

    Returns:
        Task: The task if found
        None: If no task with that ID exists

    Example:
        task = get_task(session, task_id=1)
        if task:
            print(task.title)
        else:
            print("Task not found")

    What happens:
        1. session.get() looks up by primary key
        2. Returns Task object if found, None if not
    """
    # session.get() is the fastest way to get by primary key
    # It first checks if task is already in session cache
    # Then queries database if not cached
    return session.get(Task, task_id)


def get_tasks(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Get a list of tasks with pagination.

    Args:
        session: Database session
        skip: Number of tasks to skip (for pagination)
        limit: Maximum number of tasks to return

    Returns:
        List[Task]: List of task objects

    Example:
        # Get first 10 tasks
        tasks = get_tasks(session, skip=0, limit=10)

        # Get next 10 tasks (page 2)
        tasks = get_tasks(session, skip=10, limit=10)

    What happens:
        1. select(Task) creates a SELECT query
        2. offset(skip) skips first N results
        3. limit(limit) caps maximum results
        4. session.exec() runs the query
        5. .all() converts to list

    Pagination explained:
        skip=0, limit=10  → Tasks 1-10
        skip=10, limit=10 → Tasks 11-20
        skip=20, limit=10 → Tasks 21-30
    """
    # Build the query
    # select(Task) = "SELECT * FROM task"
    statement = select(Task).offset(skip).limit(limit)

    # Execute query and get all results as a list
    results = session.exec(statement)

    return results.all()


# ----------------------------------------------------------------------------
# UPDATE OPERATION
# ----------------------------------------------------------------------------
#
# WHAT IT DOES:
#   Modifies an existing task with new data.
#
# IMPORTANT:
#   - Only updates fields that are provided (not None)
#   - Automatically updates the updated_at timestamp
#   - Returns None if task doesn't exist
#

def update_task(
    session: Session,
    task_id: int,
    task_data: TaskUpdate
) -> Optional[Task]:
    """
    Update an existing task.

    Args:
        session: Database session
        task_id: ID of task to update
        task_data: TaskUpdate schema with fields to change

    Returns:
        Task: The updated task if found
        None: If no task with that ID exists

    Example:
        # Update only the status
        update_data = TaskUpdate(status="completed")
        updated_task = update_task(session, task_id=1, task_data=update_data)

        # Update multiple fields
        update_data = TaskUpdate(title="New Title", priority="high")
        updated_task = update_task(session, task_id=1, task_data=update_data)

    What happens:
        1. Find the task by ID
        2. If not found, return None
        3. Loop through provided fields
        4. Update only non-None fields
        5. Update the updated_at timestamp
        6. Commit and refresh
    """
    # First, get the existing task
    task = session.get(Task, task_id)

    # If task doesn't exist, return None
    # Router will convert this to 404 Not Found
    if not task:
        return None

    # Get update data as dictionary, excluding unset fields
    # exclude_unset=True means: only include fields that were actually provided
    # This allows partial updates (only change what user sends)
    update_dict = task_data.model_dump(exclude_unset=True)

    # Update each provided field
    for field, value in update_dict.items():
        # setattr() sets an attribute on an object
        # setattr(task, "title", "New Title") is same as task.title = "New Title"
        setattr(task, field, value)

    # Always update the updated_at timestamp
    task.updated_at = datetime.now(timezone.utc)

    # Add to session (mark as modified)
    session.add(task)

    # Commit changes to database
    session.commit()

    # Refresh to get any database-side changes
    session.refresh(task)

    return task


# ----------------------------------------------------------------------------
# DELETE OPERATION
# ----------------------------------------------------------------------------
#
# WHAT IT DOES:
#   Removes a task from the database permanently.
#
# WARNING:
#   This is permanent! Once deleted, data cannot be recovered.
#   In production, consider "soft delete" (mark as deleted, don't remove).
#

def delete_task(session: Session, task_id: int) -> bool:
    """
    Delete a task from the database.

    Args:
        session: Database session
        task_id: ID of task to delete

    Returns:
        True: If task was found and deleted
        False: If no task with that ID exists

    Example:
        if delete_task(session, task_id=1):
            print("Task deleted successfully")
        else:
            print("Task not found")

    What happens:
        1. Find the task by ID
        2. If not found, return False
        3. Delete the task
        4. Commit the deletion
        5. Return True

    Security note:
        In production, consider "soft delete":
        - Add a "deleted" boolean field
        - Set to True instead of actually deleting
        - Allows recovery of accidentally deleted data
    """
    # Find the task
    task = session.get(Task, task_id)

    # If task doesn't exist, return False
    if not task:
        return False

    # Delete the task
    session.delete(task)

    # Commit the deletion
    session.commit()

    return True


# ----------------------------------------------------------------------------
# WHAT YOU LEARNED IN THIS FILE
# ----------------------------------------------------------------------------
#
# 1. CRUD PATTERN:
#    - Create: session.add() + commit() + refresh()
#    - Read: session.get() for one, select().exec().all() for many
#    - Update: get, modify fields, add, commit, refresh
#    - Delete: get, session.delete(), commit
#
# 2. SESSION OPERATIONS:
#    - session.add(obj): Mark for insert/update
#    - session.commit(): Save all changes
#    - session.refresh(obj): Update with DB values
#    - session.delete(obj): Mark for deletion
#    - session.get(Model, id): Get by primary key
#    - session.exec(statement): Run a query
#
# 3. QUERY BUILDING:
#    - select(Model): Start a SELECT query
#    - .offset(n): Skip first n rows
#    - .limit(n): Return max n rows
#
# 4. PARTIAL UPDATES:
#    - model_dump(exclude_unset=True): Only provided fields
#    - setattr(): Dynamically set attributes
#
# 5. RETURN VALUES:
#    - Return object when found
#    - Return None when not found
#    - Router converts None to 404
#
# ============================================================================
