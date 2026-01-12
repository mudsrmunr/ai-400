# ============================================================================
# SCHEMAS PACKAGE INITIALIZATION
# ============================================================================
#
# WHAT IS THIS FILE?
#   Makes the "schemas" folder a Python package.
#   Exports all schemas for easy importing.
#
# WHAT ARE SCHEMAS?
#   Schemas define the SHAPE of data for API operations:
#   - What fields are required when CREATING data
#   - What fields are optional when UPDATING data
#   - What fields are returned when READING data
#
# WHY SEPARATE FROM MODELS?
#   - Models = database structure (all fields)
#   - Schemas = API contract (only relevant fields per operation)
#
# ============================================================================

# Import all task schemas for easy access
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskList
)

# Export list
__all__ = [
    "TaskCreate",
    "TaskUpdate",
    "TaskRead",
    "TaskList"
]
