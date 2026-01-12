# ============================================================================
# TASK API TESTS (test_tasks.py)
# ============================================================================
#
# WHAT IS THIS FILE?
#   Contains tests for all Task API endpoints.
#   Verifies that CRUD operations work correctly.
#
# HOW TO RUN TESTS:
#   pytest                    # Run all tests
#   pytest -v                 # Verbose output
#   pytest tests/test_tasks.py  # Run only this file
#   pytest -k "test_create"   # Run tests matching pattern
#
# TEST NAMING:
#   test_<operation>_<scenario>
#   Example: test_create_task_success
#
# ASSERTIONS:
#   assert condition          # Fails if condition is False
#   assert a == b            # Fails if a doesn't equal b
#
# ============================================================================


# ----------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------

# pytest for testing
import pytest


# ============================================================================
# CREATE TESTS (POST /tasks)
# ============================================================================

class TestCreateTask:
    """Tests for creating tasks (POST /tasks)."""

    def test_create_task_success(self, client):
        """
        Test creating a task with valid data.

        GIVEN: Valid task data
        WHEN: POST /tasks is called
        THEN: Task is created with status 201
        """
        # Arrange: Prepare test data
        task_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high"
        }

        # Act: Make the request
        response = client.post("/tasks/", json=task_data)

        # Assert: Check the response
        assert response.status_code == 201  # Created

        # Check response data
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["priority"] == "high"
        assert data["status"] == "pending"  # Default value
        assert "id" in data  # ID should be generated
        assert "created_at" in data  # Timestamp should exist
        assert "updated_at" in data  # Timestamp should exist

    def test_create_task_minimal(self, client):
        """
        Test creating a task with only required fields.

        GIVEN: Only title (required field)
        WHEN: POST /tasks is called
        THEN: Task is created with defaults for optional fields
        """
        # Only title is required
        task_data = {"title": "Minimal task"}

        response = client.post("/tasks/", json=task_data)

        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Minimal task"
        assert data["description"] is None  # Default
        assert data["status"] == "pending"  # Default
        assert data["priority"] == "medium"  # Default

    def test_create_task_without_title_fails(self, client):
        """
        Test that creating a task without title fails.

        GIVEN: Task data without title
        WHEN: POST /tasks is called
        THEN: Request fails with 422 (validation error)
        """
        # Missing required field: title
        task_data = {"description": "No title provided"}

        response = client.post("/tasks/", json=task_data)

        # 422 = Unprocessable Entity (validation failed)
        assert response.status_code == 422

    def test_create_task_with_invalid_status_fails(self, client):
        """
        Test that invalid status value is rejected.

        GIVEN: Task data with invalid status
        WHEN: POST /tasks is called
        THEN: Request fails with 422 (validation error)
        """
        task_data = {
            "title": "Test task",
            "status": "invalid_status"  # Not a valid enum value
        }

        response = client.post("/tasks/", json=task_data)

        assert response.status_code == 422


# ============================================================================
# READ TESTS (GET /tasks, GET /tasks/{id})
# ============================================================================

class TestReadTasks:
    """Tests for reading tasks (GET endpoints)."""

    def test_read_tasks_empty(self, client):
        """
        Test getting tasks when database is empty.

        GIVEN: No tasks in database
        WHEN: GET /tasks is called
        THEN: Returns empty list with count 0
        """
        response = client.get("/tasks/")

        assert response.status_code == 200

        data = response.json()
        assert data["tasks"] == []
        assert data["count"] == 0

    def test_read_tasks_with_data(self, client, sample_task):
        """
        Test getting tasks when database has data.

        GIVEN: One task exists (from sample_task fixture)
        WHEN: GET /tasks is called
        THEN: Returns list with one task
        """
        response = client.get("/tasks/")

        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 1
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"

    def test_read_single_task_success(self, client, sample_task):
        """
        Test getting a single task by ID.

        GIVEN: A task exists
        WHEN: GET /tasks/{id} is called
        THEN: Returns the task
        """
        task_id = sample_task["id"]

        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    def test_read_single_task_not_found(self, client):
        """
        Test getting a task that doesn't exist.

        GIVEN: No task with ID 999
        WHEN: GET /tasks/999 is called
        THEN: Returns 404 Not Found
        """
        response = client.get("/tasks/999")

        assert response.status_code == 404

        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_read_tasks_pagination(self, client):
        """
        Test pagination with skip and limit.

        GIVEN: Multiple tasks exist
        WHEN: GET /tasks with skip/limit params
        THEN: Returns correct subset
        """
        # Create 5 tasks
        for i in range(5):
            client.post("/tasks/", json={"title": f"Task {i}"})

        # Get first 2 tasks
        response = client.get("/tasks/?skip=0&limit=2")
        data = response.json()
        assert len(data["tasks"]) == 2

        # Get next 2 tasks
        response = client.get("/tasks/?skip=2&limit=2")
        data = response.json()
        assert len(data["tasks"]) == 2


# ============================================================================
# UPDATE TESTS (PUT /tasks/{id})
# ============================================================================

class TestUpdateTask:
    """Tests for updating tasks (PUT /tasks/{id})."""

    def test_update_task_success(self, client, sample_task):
        """
        Test updating a task with valid data.

        GIVEN: A task exists
        WHEN: PUT /tasks/{id} is called with new data
        THEN: Task is updated successfully
        """
        task_id = sample_task["id"]

        update_data = {
            "title": "Updated Title",
            "status": "completed"
        }

        response = client.put(f"/tasks/{task_id}", json=update_data)

        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "completed"
        # Description should remain unchanged
        assert data["description"] == "A task for testing"

    def test_update_task_partial(self, client, sample_task):
        """
        Test partial update (only some fields).

        GIVEN: A task exists
        WHEN: PUT /tasks/{id} with only status
        THEN: Only status changes, other fields unchanged
        """
        task_id = sample_task["id"]
        original_title = sample_task["title"]

        # Only update status
        update_data = {"status": "in_progress"}

        response = client.put(f"/tasks/{task_id}", json=update_data)

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "in_progress"
        assert data["title"] == original_title  # Unchanged

    def test_update_task_not_found(self, client):
        """
        Test updating a task that doesn't exist.

        GIVEN: No task with ID 999
        WHEN: PUT /tasks/999 is called
        THEN: Returns 404 Not Found
        """
        update_data = {"title": "New Title"}

        response = client.put("/tasks/999", json=update_data)

        assert response.status_code == 404

    def test_update_task_invalid_data(self, client, sample_task):
        """
        Test updating with invalid data.

        GIVEN: A task exists
        WHEN: PUT with invalid status
        THEN: Returns 422 validation error
        """
        task_id = sample_task["id"]

        update_data = {"status": "invalid_status"}

        response = client.put(f"/tasks/{task_id}", json=update_data)

        assert response.status_code == 422


# ============================================================================
# DELETE TESTS (DELETE /tasks/{id})
# ============================================================================

class TestDeleteTask:
    """Tests for deleting tasks (DELETE /tasks/{id})."""

    def test_delete_task_success(self, client, sample_task):
        """
        Test deleting a task.

        GIVEN: A task exists
        WHEN: DELETE /tasks/{id} is called
        THEN: Task is deleted (204 No Content)
        """
        task_id = sample_task["id"]

        response = client.delete(f"/tasks/{task_id}")

        # 204 = No Content (success, nothing to return)
        assert response.status_code == 204

        # Verify task is gone
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client):
        """
        Test deleting a task that doesn't exist.

        GIVEN: No task with ID 999
        WHEN: DELETE /tasks/999 is called
        THEN: Returns 404 Not Found
        """
        response = client.delete("/tasks/999")

        assert response.status_code == 404


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """
        Test the root endpoint returns health status.

        GIVEN: The API is running
        WHEN: GET / is called
        THEN: Returns health check information
        """
        response = client.get("/")

        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "healthy"


# ============================================================================
# WHAT YOU LEARNED IN THIS FILE
# ============================================================================
#
# 1. TEST STRUCTURE:
#    - Classes group related tests
#    - test_* functions are discovered by pytest
#    - Arrange → Act → Assert pattern
#
# 2. ASSERTIONS:
#    - assert condition: Fails if False
#    - assert a == b: Equality check
#    - "in" for checking substrings
#
# 3. HTTP STATUS CODES:
#    - 200 OK: Success (GET, PUT)
#    - 201 Created: Success (POST)
#    - 204 No Content: Success (DELETE)
#    - 404 Not Found: Resource doesn't exist
#    - 422 Unprocessable Entity: Validation failed
#
# 4. FIXTURES:
#    - client: Makes HTTP requests
#    - sample_task: Pre-created task for tests
#
# 5. TEST CLIENT:
#    - client.get("/path")
#    - client.post("/path", json={...})
#    - client.put("/path", json={...})
#    - client.delete("/path")
#    - response.status_code, response.json()
#
# ============================================================================
