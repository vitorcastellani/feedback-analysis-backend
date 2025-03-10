from model import Feedback, Campaign

def test_create_feedback(client, db_session):
    """Test creating a new feedback entry with a campaign reference."""
    campaign = Campaign(name="Test Campaign", description="Campaign for feedback test")
    db_session.add(campaign)
    db_session.commit()
    
    response = client.post("/api/feedback", json={"message": "Great service!", "campaign_id": campaign.id})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["message"] == "Great service!"
    assert data["campaign_id"] == campaign.id
    assert data["created_at"] is not None

def test_get_feedbacks(client):
    """Test retrieving all feedback entries with pagination."""
    response = client.get("/api/feedbacks?limit=10&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "items" in data

def test_get_feedback_by_id(client, db_session):
    """Test retrieving a single feedback entry by ID."""
    campaign = Campaign(name="Another Test Campaign", description="Campaign for single feedback test")
    db_session.add(campaign)
    db_session.commit()
    
    feedback = Feedback(message="Test feedback", campaign_id=campaign.id)
    db_session.add(feedback)
    db_session.commit()

    response = client.get(f"/api/feedback/{feedback.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == feedback.id
    assert data["message"] == "Test feedback"
    assert data["campaign_id"] == campaign.id
    assert data["created_at"] is not None

def test_delete_feedback(client, db_session):
    """Test deleting a feedback entry by ID."""
    campaign = Campaign(name="Delete Campaign", description="Campaign for feedback delete test")
    db_session.add(campaign)
    db_session.commit()
    
    feedback = Feedback(message="To be deleted", campaign_id=campaign.id)
    db_session.add(feedback)
    db_session.commit()

    response = client.delete(f"/api/feedback/{feedback.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Feedback was removed"

    response = client.get(f"/api/feedback/{feedback.id}")
    assert response.status_code == 404