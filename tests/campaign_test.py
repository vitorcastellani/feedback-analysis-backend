from model import Campaign


def test_create_campaign(client, db_session):
    """
    Test creating a new campaign entry.
    """
    response = client.post("/api/campaign", json={
        "name": "Test Campaign",
        "description": "This is a test campaign.",
        "active": True,
        "multiple_answers_from_user": False,
        "max_answers": 10
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["name"] == "Test Campaign"
    assert data["description"] == "This is a test campaign."
    assert data["active"] is True
    assert data["multiple_answers_from_user"] is False
    assert data["max_answers"] == 10
    assert data["created_at"] is not None


def test_update_campaign(client, db_session):
    """
    Test updating a campaign entry by ID.
    """
    campaign = Campaign(
        name="Original Campaign",
        description="Original description",
        active=True,
        multiple_answers_from_user=True,
        max_answers=5,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    response = client.put(f"/api/campaign/{campaign.id}", json={
        "name": "Updated Campaign",
        "description": "Updated description",
        "active": False,
        "multiple_answers_from_user": False,
        "max_answers": 20
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == campaign.id
    assert data["name"] == "Updated Campaign"
    assert data["description"] == "Updated description"
    assert data["active"] is False
    assert data["multiple_answers_from_user"] is False
    assert data["max_answers"] == 20


def test_get_campaigns(client, db_session):
    """
    Test retrieving all campaign entries with pagination.
    """
    response = client.get("/api/campaigns?limit=10&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_campaign_by_id(client, db_session):
    """
    Test retrieving a single campaign entry by ID.
    """
    campaign = Campaign(
        name="Campaign Test",
        description="Testing get campaign by ID",
        active=True,
        multiple_answers_from_user=True,
        max_answers=10,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    response = client.get(f"/api/campaign/{campaign.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == campaign.id
    assert data["name"] == "Campaign Test"
    assert data["description"] == "Testing get campaign by ID"
    assert data["active"] is True
    assert data["multiple_answers_from_user"] is True
    assert data["max_answers"] == 10
    assert data["short_code"] == "TEST"
    assert data["feedback_count"] == 0
    assert data["created_at"] is not None


def test_get_campaign_by_short_code(client, db_session):
    """
    Test retrieving a single campaign entry by short code.
    """
    campaign = Campaign(
        name="Short Code Test",
        description="Testing get campaign by short code",
        active=True,
        multiple_answers_from_user=True,
        max_answers=10,
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    response = client.get(f"/api/campaign/short_code/{campaign.short_code}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == campaign.id
    assert data["name"] == "Short Code Test"
    assert data["description"] == "Testing get campaign by short code"
    assert data["active"] is True
    assert data["multiple_answers_from_user"] is True
    assert data["max_answers"] == 10
    assert data["short_code"] == "TEST"
    assert data["feedback_count"] == 0
    assert data["created_at"] is not None


def test_delete_campaign(client, db_session):
    """
    Test deleting a campaign entry by ID.
    """
    campaign = Campaign(
        name="Delete Test Campaign",
        description="This campaign will be deleted",
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    response = client.delete(f"/api/campaign/{campaign.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Campaign deleted"

    response = client.get(f"/api/campaign/{campaign.id}")
    assert response.status_code == 404