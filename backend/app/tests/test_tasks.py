import pytest
from datetime import datetime


class TestTasksAPI:
    """Test suite for Task API endpoints."""
    
    def test_create_task_success(self, client):
        """Test successful POST /tasks."""
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00142",
            "thread_id": "th_0091",
            "title": "RFP — Enterprise DMS for Meridian Steel",
            "description": "Test description",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "due_date": "2026-08-12",
            "deal_value_inr": 2500000,
            "company_name": "Meridian Steel Pvt Ltd",
            "confidence": 0.91
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "task_id" in data
        assert data["candidate_id"] == "test@example.com"
        assert data["source_email_id"] == "em_00142"
        assert "created_at" in data
    
    def test_invalid_assignee_id(self, client):
        """Test POST /tasks with invalid assignee_id."""
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00143",
            "thread_id": "th_0092",
            "title": "Test Task",
            "assignee_id": "Aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422  # Pydantic validation error for Literal types
    
    def test_invalid_category(self, client):
        """Test POST /tasks with invalid category."""
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00144",
            "thread_id": "th_0093",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "invalid_category",
            "priority": "high",
            "confidence": 0.91
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422  # Pydantic validation error for Literal types
    
    def test_invalid_priority(self, client):
        """Test POST /tasks with invalid priority."""
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00145",
            "thread_id": "th_0094",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "urgent",
            "confidence": 0.91
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422  # Pydantic validation error for Literal types
    
    def test_invalid_confidence(self, client):
        """Test POST /tasks with invalid confidence (out of range)."""
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00146",
            "thread_id": "th_0095",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 1.5
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_get_tasks(self, client):
        """Test GET /tasks."""
        # First create a task
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00147",
            "thread_id": "th_0096",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        client.post("/tasks", json=task_data)
        
        # Get tasks
        response = client.get("/tasks?candidate_id=test@example.com")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["candidate_id"] == "test@example.com"
    
    def test_get_tasks_with_thread_id_filter(self, client):
        """Test GET /tasks with thread_id filter."""
        # Create tasks with different thread_ids
        task_data1 = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00148",
            "thread_id": "th_0097",
            "title": "Test Task 1",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        task_data2 = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00149",
            "thread_id": "th_0098",
            "title": "Test Task 2",
            "assignee_id": "u_rohit",
            "category": "smb_enquiry",
            "priority": "medium",
            "confidence": 0.85
        }
        client.post("/tasks", json=task_data1)
        client.post("/tasks", json=task_data2)
        
        # Filter by thread_id
        response = client.get("/tasks?candidate_id=test@example.com&thread_id=th_0097")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert all(task["thread_id"] == "th_0097" for task in data)
    
    def test_get_tasks_with_source_email_id_filter(self, client):
        """Test GET /tasks with source_email_id filter."""
        # Create a task
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00150",
            "thread_id": "th_0099",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        client.post("/tasks", json=task_data)
        
        # Filter by source_email_id
        response = client.get("/tasks?candidate_id=test@example.com&source_email_id=em_00150")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["source_email_id"] == "em_00150"
    
    def test_patch_task(self, client):
        """Test PATCH /tasks/{task_id}."""
        # Create a task first
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00151",
            "thread_id": "th_0100",
            "title": "Original Title",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        create_response = client.post("/tasks", json=task_data)
        task_id = create_response.json()["task_id"]
        
        # Update the task
        update_data = {
            "title": "Updated Title",
            "priority": "medium"
        }
        response = client.patch(f"/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "medium"
        assert data["task_id"] == task_id
    
    def test_delete_task(self, client):
        """Test DELETE /tasks/{task_id}."""
        # Create a task first
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00152",
            "thread_id": "th_0101",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        create_response = client.post("/tasks", json=task_data)
        task_id = create_response.json()["task_id"]
        
        # Delete the task
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get("/tasks?candidate_id=test@example.com")
        tasks = get_response.json()
        assert not any(task["task_id"] == task_id for task in tasks)
    
    def test_delete_nonexistent_task(self, client):
        """Test DELETE /tasks/{task_id} with nonexistent task."""
        response = client.delete("/tasks/nonexistent_id")
        assert response.status_code == 404
    
    def test_get_users(self, client):
        """Test GET /users."""
        response = client.get("/users")
        assert response.status_code == 200
        
        data = response.json()
        assert "team" in data
        assert isinstance(data["team"], list)
        assert len(data["team"]) == 6
        
        # Check specific user
        aarti = next((user for user in data["team"] if user["user_id"] == "u_aarti"), None)
        assert aarti is not None
        assert aarti["name"] == "Aarti Menon"
        assert aarti["department"] == "Sales — Enterprise"
    
    def test_duplicate_source_email_id_protection(self, client):
        """Test that duplicate source_email_id for same candidate is prevented."""
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00153",
            "thread_id": "th_0102",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        
        # Create first task
        response1 = client.post("/tasks", json=task_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/tasks", json=task_data)
        assert response2.status_code == 409
    
    def test_candidate_id_normalization(self, client):
        """Test that candidate_id is normalized (lowercase, trimmed)."""
        task_data = {
            "candidate_id": "  TEST@EXAMPLE.COM  ",
            "source_email_id": "em_00154",
            "thread_id": "th_0103",
            "title": "Test Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["candidate_id"] == "test@example.com"
        
        # Verify it's stored correctly
        get_response = client.get("/tasks?candidate_id=test@example.com")
        tasks = get_response.json()
        assert len(tasks) >= 1
        assert tasks[0]["candidate_id"] == "test@example.com"
    
    def test_get_tasks_different_candidate_isolation(self, client):
        """Test that GET /tasks only returns tasks for the specified candidate."""
        # Create task for candidate1
        task_data1 = {
            "candidate_id": "candidate1@example.com",
            "source_email_id": "em_00155",
            "thread_id": "th_0104",
            "title": "Task for Candidate 1",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        client.post("/tasks", json=task_data1)
        
        # Create task for candidate2
        task_data2 = {
            "candidate_id": "candidate2@example.com",
            "source_email_id": "em_00156",
            "thread_id": "th_0105",
            "title": "Task for Candidate 2",
            "assignee_id": "u_rohit",
            "category": "smb_enquiry",
            "priority": "medium",
            "confidence": 0.85
        }
        client.post("/tasks", json=task_data2)
        
        # Get tasks for candidate1 only
        response = client.get("/tasks?candidate_id=candidate1@example.com")
        assert response.status_code == 200
        
        data = response.json()
        assert all(task["candidate_id"] == "candidate1@example.com" for task in data)
        assert not any(task["candidate_id"] == "candidate2@example.com" for task in data)
    
    def test_patch_cannot_modify_protected_fields(self, client):
        """Test that PATCH cannot modify candidate_id or source_email_id."""
        # Create a task first
        task_data = {
            "candidate_id": "test@example.com",
            "source_email_id": "em_00157",
            "thread_id": "th_0106",
            "title": "Original Title",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.91
        }
        create_response = client.post("/tasks", json=task_data)
        task_id = create_response.json()["task_id"]
        original_candidate_id = create_response.json()["candidate_id"]
        original_source_email_id = create_response.json()["source_email_id"]
        
        # Try to update with candidate_id and source_email_id (these should be rejected by schema)
        update_data = {
            "candidate_id": "different@example.com",
            "source_email_id": "em_99999",
            "title": "Updated Title"
        }
        response = client.patch(f"/tasks/{task_id}", json=update_data)
        # Pydantic should reject unknown fields
        assert response.status_code == 422
        
        # Verify protected fields remain unchanged by updating only allowed fields
        update_data_allowed = {
            "title": "Updated Title"
        }
        response = client.patch(f"/tasks/{task_id}", json=update_data_allowed)
        assert response.status_code == 200
        
        data = response.json()
        # Verify protected fields were not changed
        assert data["candidate_id"] == original_candidate_id
        assert data["source_email_id"] == original_source_email_id
        # Verify other field was updated
        assert data["title"] == "Updated Title"
