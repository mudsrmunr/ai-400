# ============================================================================
# CRUD PACKAGE INITIALIZATION
# ============================================================================
#
# WHAT IS THIS FILE?
#   Makes the "crud" folder a Python package.
#   Exports all CRUD functions for easy importing.
#
# WHAT IS CRUD?
#   CRUD = Create, Read, Update, Delete
#   The four basic operations for working with data.
#
# WHY A SEPARATE FOLDER?
#   - Keeps database logic separate from API logic
#   - Reusable across different parts of the app
#   - Easier to test (can test CRUD without HTTP)
#
# ============================================================================

# Import all task CRUD functions for easy access
from app.crud.task import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task
)

# Export list
__all__ = [
    "create_task",
    "get_task",
    "get_tasks",
    "update_task",
    "delete_task"
]
