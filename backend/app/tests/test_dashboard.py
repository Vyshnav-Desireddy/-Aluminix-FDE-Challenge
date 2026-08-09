import pytest
from app.schemas.task import TaskCreate


class TestDashboardAPI:
    """Test suite for dashboard API endpoints."""
    
    def test_get_dashboard_tasks_uses_candidate_id(self, client):
        """Test that GET /api/tasks uses CANDIDATE_ID from configuration."""
        # Create a task for the configured candidate
        from app.config import settings
        task_data = {
            "candidate_id": settings.CANDIDATE_ID,
            "source_email_id": "em_dashboard_001",
            "thread_id": "th_dashboard_001",
            "title": "Dashboard Test Task",
            "description": "Test task for dashboard endpoint",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.85
        }
        
        create_response = client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        # Get tasks via dashboard endpoint (no candidate_id parameter needed)
        response = client.get("/api/tasks")
        assert response.status_code == 200
        
        tasks = response.json()
        assert len(tasks) > 0
        
        # Verify the task we created is in the results
        created_task_ids = [t["task_id"] for t in tasks]
        task_id = create_response.json()["task_id"]
        assert task_id in created_task_ids
    
    def test_get_dashboard_tasks_with_thread_filter(self, client):
        """Test that GET /api/tasks can filter by thread_id."""
        from app.config import settings
        
        # Create tasks with different thread IDs
        task1_data = {
            "candidate_id": settings.CANDIDATE_ID,
            "source_email_id": "em_dashboard_thread1",
            "thread_id": "thread_a",
            "title": "Thread A Task",
            "assignee_id": "u_rohit",
            "category": "smb_enquiry",
            "priority": "medium",
            "confidence": 0.75
        }
        
        task2_data = {
            "candidate_id": settings.CANDIDATE_ID,
            "source_email_id": "em_dashboard_thread2",
            "thread_id": "thread_b",
            "title": "Thread B Task",
            "assignee_id": "u_meera",
            "category": "marketing",
            "priority": "low",
            "confidence": 0.65
        }
        
        client.post("/tasks", json=task1_data)
        client.post("/tasks", json=task2_data)
        
        # Filter by thread_a
        response = client.get("/api/tasks?thread_id=thread_a")
        assert response.status_code == 200
        
        tasks = response.json()
        assert all(t["thread_id"] == "thread_a" for t in tasks)
    
    def test_get_dashboard_tasks_with_assignee_filter(self, client):
        """Test that GET /api/tasks can filter by assignee_id."""
        from app.config import settings
        
        # Create tasks with different assignees
        task1_data = {
            "candidate_id": settings.CANDIDATE_ID,
            "source_email_id": "em_dashboard_assignee1",
            "thread_id": "th_assignee_test",
            "title": "Aarti Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.9
        }
        
        task2_data = {
            "candidate_id": settings.CANDIDATE_ID,
            "source_email_id": "em_dashboard_assignee2",
            "thread_id": "th_assignee_test",
            "title": "Rohit Task",
            "assignee_id": "u_rohit",
            "category": "smb_enquiry",
            "priority": "medium",
            "confidence": 0.8
        }
        
        client.post("/tasks", json=task1_data)
        client.post("/tasks", json=task2_data)
        
        # Filter by u_aarti
        response = client.get("/api/tasks?assignee_id=u_aarti")
        assert response.status_code == 200
        
        tasks = response.json()
        assert all(t["assignee_id"] == "u_aarti" for t in tasks)
    
    def test_get_dashboard_tasks_empty_for_different_candidate(self, client):
        """Test that GET /api/tasks only returns tasks for configured CANDIDATE_ID."""
        from app.config import settings
        
        # Create a task for a different candidate
        other_candidate = "other@example.com"
        task_data = {
            "candidate_id": other_candidate,
            "source_email_id": "em_other_candidate",
            "thread_id": "th_other",
            "title": "Other Candidate Task",
            "assignee_id": "u_triage",
            "category": "triage",
            "priority": "low",
            "confidence": 0.5
        }
        
        client.post("/tasks", json=task_data)
        
        # Get tasks via dashboard endpoint
        response = client.get("/api/tasks")
        assert response.status_code == 200
        
        tasks = response.json()
        # Should not include the task from other candidate
        assert not any(t["candidate_id"] == other_candidate for t in tasks)


class TestStatsAPI:
    """Test suite for statistics API endpoint."""
    
    def test_get_stats_empty(self, client):
        """Test that GET /api/stats returns zero stats when no tasks exist."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert stats["total_tasks"] == 0
        assert stats["by_category"] == {}
        assert stats["by_assignee"] == {}
        assert stats["by_priority"] == {}
        assert stats["total_deal_value_inr"] == 0
        assert stats["average_confidence"] == 0.0
    
    def test_get_stats_with_tasks(self, client):
        """Test that GET /api/stats correctly aggregates task statistics."""
        from app.config import settings
        
        # Create multiple tasks with different properties
        tasks_data = [
            {
                "candidate_id": settings.CANDIDATE_ID,
                "source_email_id": "em_stats_001",
                "thread_id": "th_stats_001",
                "title": "Enterprise RFP Task",
                "assignee_id": "u_aarti",
                "category": "enterprise_rfp",
                "priority": "high",
                "deal_value_inr": 1500000,
                "confidence": 0.85
            },
            {
                "candidate_id": settings.CANDIDATE_ID,
                "source_email_id": "em_stats_002",
                "thread_id": "th_stats_002",
                "title": "SMB Enquiry Task",
                "assignee_id": "u_rohit",
                "category": "smb_enquiry",
                "priority": "medium",
                "deal_value_inr": 500000,
                "confidence": 0.75
            },
            {
                "candidate_id": settings.CANDIDATE_ID,
                "source_email_id": "em_stats_003",
                "thread_id": "th_stats_003",
                "title": "Marketing Task",
                "assignee_id": "u_meera",
                "category": "marketing",
                "priority": "low",
                "deal_value_inr": None,
                "confidence": 0.65
            }
        ]
        
        for task_data in tasks_data:
            client.post("/tasks", json=task_data)
        
        # Get stats
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        stats = response.json()
        
        # Verify total count
        assert stats["total_tasks"] == 3
        
        # Verify category breakdown
        assert stats["by_category"]["enterprise_rfp"] == 1
        assert stats["by_category"]["smb_enquiry"] == 1
        assert stats["by_category"]["marketing"] == 1
        
        # Verify assignee breakdown
        assert stats["by_assignee"]["u_aarti"] == 1
        assert stats["by_assignee"]["u_rohit"] == 1
        assert stats["by_assignee"]["u_meera"] == 1
        
        # Verify priority breakdown
        assert stats["by_priority"]["high"] == 1
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1
        
        # Verify deal value sum
        assert stats["total_deal_value_inr"] == 2000000
        
        # Verify average confidence
        expected_avg = (0.85 + 0.75 + 0.65) / 3
        assert abs(stats["average_confidence"] - expected_avg) < 0.01
    
    def test_get_stats_uses_candidate_id(self, client):
        """Test that GET /api/stats only includes tasks for configured CANDIDATE_ID."""
        from app.config import settings
        
        # Create task for configured candidate
        task_data = {
            "candidate_id": settings.CANDIDATE_ID,
            "source_email_id": "em_stats_candidate",
            "thread_id": "th_stats_candidate",
            "title": "Configured Candidate Task",
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": "high",
            "confidence": 0.9
        }
        client.post("/tasks", json=task_data)
        
        # Create task for different candidate
        other_task_data = {
            "candidate_id": "other@example.com",
            "source_email_id": "em_stats_other",
            "thread_id": "th_stats_other",
            "title": "Other Candidate Task",
            "assignee_id": "u_rohit",
            "category": "smb_enquiry",
            "priority": "medium",
            "confidence": 0.8
        }
        client.post("/tasks", json=other_task_data)
        
        # Get stats
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        stats = response.json()
        
        # Should only include the configured candidate's task
        assert stats["total_tasks"] == 1
        assert stats["by_category"]["enterprise_rfp"] == 1
        assert "smb_enquiry" not in stats["by_category"]
