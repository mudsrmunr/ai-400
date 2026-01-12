# ============================================================================
# ROUTERS PACKAGE INITIALIZATION
# ============================================================================
#
# WHAT IS THIS FILE?
#   Makes the "routers" folder a Python package.
#   Exports all routers for registration in main.py.
#
# WHAT IS A ROUTER?
#   A collection of related API endpoints.
#   Groups endpoints by feature (tasks, users, etc.)
#
# WHY SEPARATE ROUTERS?
#   - Organization: Keep related endpoints together
#   - Modularity: Easy to add/remove features
#   - Maintainability: Each router in its own file
#
# ============================================================================

# Import the tasks router
from app.routers.tasks import router as tasks_router

# Export list
__all__ = ["tasks_router"]
