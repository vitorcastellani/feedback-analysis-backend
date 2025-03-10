from model import Campaign

def test_create_campaign(client, db_session):
    """Test creating a new campaign entry."""
    response = client.post("/api/campaign", json={
        "name": "Test Campaign",
        "description": "This is a test campaign."
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["name"] == "Test Campaign"
    assert data["description"] == "This is a test campaign."
    assert data["created_at"] is not None

def test_get_campaigns(client, db_session):
    """Test retrieving all campaign entries with pagination."""
    response = client.get("/api/campaigns?limit=10&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_campaign_by_id(client, db_session):
    """Test retrieving a single campaign entry by ID."""
    campaign = Campaign(name="Campaign Test", description="Testing get campaign by ID")
    db_session.add(campaign)
    db_session.commit()
    
    response = client.get(f"/api/campaign/{campaign.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == campaign.id
    assert data["name"] == "Campaign Test"
    assert data["description"] == "Testing get campaign by ID"
    assert data["created_at"] is not None

def test_delete_campaign(client, db_session):
    """Test deleting a campaign entry by ID."""
    campaign = Campaign(name="Delete Test Campaign", description="This campaign will be deleted")
    db_session.add(campaign)
    db_session.commit()
    
    response = client.delete(f"/api/campaign/{campaign.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Campaign deleted"
    
    response = client.get(f"/api/campaign/{campaign.id}")
    assert response.status_code == 404