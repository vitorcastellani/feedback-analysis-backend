from model import Campaign, Feedback

def test_dashboard_metrics(client, db_session):
    """Test retrieving dashboard metrics."""
    # Create sample campaigns with short_code
    campaign1 = Campaign(name="Campaign 1", active=True, short_code="ABC123")
    campaign2 = Campaign(name="Campaign 2", active=False, short_code="XYZ789")
    db_session.add_all([campaign1, campaign2])
    db_session.commit()

    # Create sample feedbacks
    feedback1 = Feedback(campaign_id=campaign1.id, message="Feedback 1")
    feedback2 = Feedback(campaign_id=campaign1.id, message="Feedback 2")
    feedback3 = Feedback(campaign_id=campaign2.id, message="Feedback 3")
    db_session.add_all([feedback1, feedback2, feedback3])
    db_session.commit()

    # Call the dashboard-metrics endpoint
    response = client.get("/api/dashboard-metrics")
    assert response.status_code == 200

    # Validate the response data
    data = response.get_json()
    assert data["total_campaigns"] == 2
    assert data["total_feedbacks"] == 3
    assert data["active_campaigns"] == 1