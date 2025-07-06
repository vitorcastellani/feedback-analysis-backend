from model import Feedback, Campaign


def test_create_feedback(client, db_session):
    """Test creating a new feedback entry with a campaign reference."""
    campaign = Campaign(
        name="Test Campaign",
        description="Campaign for feedback test",
        active=True,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    payload = {
        "message": "Great service!",
        "campaign_id": campaign.id,
        "age_range": "25-34",
        "gender": "male",
        "education_level": "bachelor",
        "country": "Brazil",
        "state": "SP"
    }

    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["message"] == "Great service!"
    assert data["campaign_id"] == campaign.id
    assert data["age_range"] == "25-34"
    assert data["gender"] == "male"
    assert data["education_level"] == "bachelor"
    assert data["country"] == "Brazil"
    assert data["state"] == "SP"
    assert data["created_at"] is not None


def test_create_feedback_inactive_campaign(client, db_session):
    """Test creating feedback for an inactive campaign."""
    campaign = Campaign(
        name="Inactive Campaign",
        description="Should fail",
        active=False,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    payload = {
        "message": "Won't work",
        "campaign_id": campaign.id,
        "age_range": "18-24",
        "gender": "female",
        "education_level": "highschool",
        "country": "Brazil",
        "state": "RJ"
    }

    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["message"] == "Campaign is not active"


def test_create_feedback_max_answers_exceeded(client, db_session):
    """Test exceeding the max_answers limit for a campaign."""
    campaign = Campaign(
        name="Limited Campaign",
        description="Max answers set to 1",
        active=True,
        max_answers=1,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    payload = {
        "message": "First answer",
        "campaign_id": campaign.id,
        "age_range": "35-44",
        "gender": "other",
        "education_level": "master",
        "country": "Brazil",
        "state": "MG"
    }

    first_response = client.post("/api/feedback", json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/api/feedback", json=payload)
    assert second_response.status_code == 400
    data = second_response.get_json()
    assert data["message"] == "Campaign has reached the maximum number of answers"


def test_create_feedback_multiple_answers_not_allowed(client, db_session):
    """Test preventing multiple feedbacks from the same user when not allowed."""
    campaign = Campaign(
        name="Single Answer Campaign",
        description="No multiple answers",
        active=True,
        multiple_answers_from_user=False,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    payload = {
        "message": "First feedback",
        "campaign_id": campaign.id,
        "age_range": "45-54",
        "gender": "female",
        "education_level": "phd",
        "country": "Brazil",
        "state": "RS"
    }

    first_response = client.post("/api/feedback", json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/api/feedback", json=payload)
    assert second_response.status_code == 400
    data = second_response.get_json()
    assert data["message"] == "Campaign does not allow multiple answers from the same user"


def test_get_feedbacks(client):
    """Test retrieving all feedback entries with pagination."""
    response = client.get("/api/feedbacks?limit=10&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "items" in data


def test_get_feedback_by_id(client, db_session):
    """Test retrieving a single feedback entry by its ID."""
    campaign = Campaign(
        name="Another Test Campaign",
        description="Campaign for single feedback test",
        active=True,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    feedback = Feedback(
        message="Test feedback",
        campaign_id=campaign.id,
        age_range="25-34",
        gender="male",
        education_level="bachelor",
        country="Brazil",
        state="SP"
    )
    db_session.add(feedback)
    db_session.commit()

    response = client.get(f"/api/feedback/{feedback.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == feedback.id
    assert data["message"] == "Test feedback"
    assert data["campaign_id"] == campaign.id
    assert data["age_range"] == "25-34"
    assert data["gender"] == "male"
    assert data["education_level"] == "bachelor"
    assert data["country"] == "Brazil"
    assert data["state"] == "SP"
    assert data["created_at"] is not None


def test_delete_feedback(client, db_session):
    """Test deleting a feedback entry by its ID."""
    campaign = Campaign(
        name="Delete Campaign",
        description="Campaign for feedback delete test",
        active=True,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    feedback = Feedback(
        message="To be deleted",
        campaign_id=campaign.id,
        age_range="18-24",
        gender="female",
        education_level="highschool",
        country="Brazil",
        state="RJ"
    )
    db_session.add(feedback)
    db_session.commit()

    response = client.delete(f"/api/feedback/{feedback.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Feedback was removed"

    response = client.get(f"/api/feedback/{feedback.id}")
    assert response.status_code == 404