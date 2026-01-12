# ============================================================================
# MODELS PACKAGE INITIALIZATION
# ============================================================================
#
# WHAT IS THIS FILE?
#   Makes the "models" folder a Python package.
#   Also serves as a convenient place to export all models.
#
# WHY EXPORT MODELS HERE?
#   Instead of: from app.models.task import Task
#   You can do:  from app.models import Task
#
#   Cleaner and easier to remember!
#
# ============================================================================

# Import Task model so it can be accessed from app.models
# This line will work after we create task.py
from app.models.task import Task

# Export list - what's available when you do "from app.models import *"
__all__ = ["Task"]
