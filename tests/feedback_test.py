import pytest
from model.feedback import Feedback
from tests import db_session, client, test_session, app

def test_create_feedback(client, db_session):
    """Test creating a new feedback entry."""
    response = client.post("/api/feedback", json={"message": "Great service!"})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["message"] == "Great service!"

def test_get_feedbacks(client):
    """Test retrieving all feedback entries with pagination."""
    response = client.get("/api/feedbacks?limit=10&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "items" in data

def test_get_feedback_by_id(client, db_session):
    """Test retrieving a single feedback entry by ID."""
    feedback = Feedback(message="Test feedback")
    db_session.add(feedback)
    db_session.commit()

    response = client.get(f"/api/feedback/{feedback.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == feedback.id
    assert data["message"] == "Test feedback"

def test_delete_feedback(client, db_session):
    """Test deleting a feedback entry by ID."""
    feedback = Feedback(message="To be deleted")
    db_session.add(feedback)
    db_session.commit()

    response = client.delete(f"/api/feedback/{feedback.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Feedback was removed"

    response = client.get(f"/api/feedback/{feedback.id}")
    assert response.status_code == 404
