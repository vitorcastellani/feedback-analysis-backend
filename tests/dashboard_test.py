from model import Campaign, Feedback, Dashboard, Component


def test_dashboard_metrics(client, db_session):
    """Test retrieving dashboard metrics, including total campaigns, feedbacks, and active campaigns."""
    campaign1 = Campaign(name="Campaign 1", active=True, short_code="ABC123")
    campaign2 = Campaign(name="Campaign 2", active=False, short_code="XYZ789")
    db_session.add_all([campaign1, campaign2])
    db_session.commit()

    feedback1 = Feedback(campaign_id=campaign1.id, message="Feedback 1")
    feedback2 = Feedback(campaign_id=campaign1.id, message="Feedback 2")
    feedback3 = Feedback(campaign_id=campaign2.id, message="Feedback 3")
    db_session.add_all([feedback1, feedback2, feedback3])
    db_session.commit()

    response = client.get("/api/dashboard-system-metrics")
    assert response.status_code == 200

    data = response.get_json()
    assert data["total_campaigns"] == 2
    assert data["total_feedbacks"] == 3
    assert data["active_campaigns"] == 1


def test_create_dashboard(client, db_session):
    """Test creating a new dashboard with campaigns and components."""
    campaign1 = Campaign(name="Campaign 1", active=True, short_code="ABC123")
    campaign2 = Campaign(name="Campaign 2", active=True, short_code="XYZ789")
    db_session.add_all([campaign1, campaign2])
    db_session.commit()

    payload = {
        "name": "Test Dashboard",
        "description": "A dashboard for testing",
        "campaign_ids": [campaign1.id, campaign2.id],
        "components": [
            {
                "name": "Bar Chart Component",
                "description": "A bar chart showing feedback counts",
                "type": "BAR_CHART",
                "settings": {
                    "x_axis": "date",
                    "y_axis": "feedback_count"
                }
            },
            {
                "name": "Pie Chart Component",
                "description": "A pie chart showing sentiment distribution",
                "type": "PIE_CHART",
                "settings": {
                    "category_column": "sentiment_category",
                    "value_column": "feedback_count"
                }
            }
        ]
    }

    response = client.post("/api/dashboard", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Dashboard"
    assert data["description"] == "A dashboard for testing"
    assert len(data["campaigns"]) == 2
    assert len(data["components"]) == 2
    assert data["components"][0]["type"] == "bar_chart"
    assert data["components"][1]["type"] == "pie_chart"


def test_list_dashboards(client, db_session):
    """Test listing all dashboards and verifying the response structure."""
    dashboard = Dashboard(name="Sample Dashboard", description="A sample dashboard")
    db_session.add(dashboard)
    db_session.commit()

    response = client.get("/api/dashboards")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "items" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Sample Dashboard"
    assert data["items"][0]["description"] == "A sample dashboard"


def test_get_dashboard(client, db_session):
    """Test retrieving a specific dashboard by its ID."""
    dashboard = Dashboard(name="Sample Dashboard", description="A sample dashboard")
    db_session.add(dashboard)
    db_session.commit()

    response = client.get(f"/api/dashboard/{dashboard.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == dashboard.id
    assert data["name"] == "Sample Dashboard"
    assert data["description"] == "A sample dashboard"


def test_update_dashboard(client, db_session):
    """Test updating an existing dashboard with new data."""
    dashboard = Dashboard(name="Old Dashboard Name", description="Old description")
    db_session.add(dashboard)
    db_session.commit()

    payload = {
        "name": "Updated Dashboard Name",
        "description": "Updated description",
        "campaign_ids": [],
        "components": [
            {
                "name": "Updated Component",
                "description": "Updated description",
                "type": "LINE_CHART",
                "settings": {
                    "x_axis": "time",
                    "y_axis": "value"
                }
            }
        ]
    }

    response = client.put(f"/api/dashboard/{dashboard.id}", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Updated Dashboard Name"
    assert data["description"] == "Updated description"
    assert len(data["components"]) == 1
    assert data["components"][0]["type"] == "line_chart"


def test_delete_dashboard(client, db_session):
    """Test deleting a dashboard and verifying it no longer exists."""
    dashboard = Dashboard(name="Dashboard to Delete", description="This dashboard will be deleted")
    db_session.add(dashboard)
    db_session.commit()

    response = client.delete(f"/api/dashboard/{dashboard.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Dashboard deleted"

    response = client.get(f"/api/dashboard/{dashboard.id}")
    assert response.status_code == 404


def test_get_component_data(client, db_session):
    """Test retrieving data for a specific component within a dashboard."""
    campaign1 = Campaign(name="Campaign 1", active=True, short_code="ABC123")
    campaign2 = Campaign(name="Campaign 2", active=True, short_code="XYZ789")
    db_session.add_all([campaign1, campaign2])
    db_session.commit()

    dashboard = Dashboard(name="Test Dashboard", description="Dashboard with components", campaigns=[campaign1, campaign2])
    db_session.add(dashboard)
    db_session.commit()

    component = Component(
        name="Bar Chart Component",
        type="BAR_CHART",
        settings={"x_axis": "id", "y_axis": "id"},
        dashboard_id=dashboard.id
    )
    db_session.add(component)
    db_session.commit()

    feedback1 = Feedback(campaign_id=campaign1.id, message="Feedback 1")
    feedback2 = Feedback(campaign_id=campaign2.id, message="Feedback 2")
    db_session.add_all([feedback1, feedback2])
    db_session.commit()

    response = client.get(f"/api/dashboard/{dashboard.id}/component/{component.id}/data")
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == component.id
    assert data["name"] == "Bar Chart Component"
    assert data["type"] == "bar_chart"
    assert "data" in data
    assert "labels" in data["data"]
    assert "values" in data["data"]