from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from config import SessionLocal
from model import Campaign, Feedback, Dashboard, Component, ComponentType
from schemas import DashboardMetricsResponse, DashboardIDParam, DashboardCreate, DashboardUpdate, DashboardResponse, DashboardListResponse
from sqlalchemy.exc import IntegrityError

# Create a new Tag
dashboard_tag = Tag(name="Dashboard", description="Operations related to dashboards.")

# Create a new Blueprint
dashboard_bp = APIBlueprint('dashboard', __name__)

# Get system metrics for the dashboard
@dashboard_bp.get("/dashboard-system-metrics", responses={200: DashboardMetricsResponse}, tags=[dashboard_tag])
def get_dashboard_metrics():
    """Get system metrics for the dashboard"""
    with SessionLocal() as db:
        total_campaigns = db.query(Campaign).count()
        total_feedbacks = db.query(Feedback).count()
        active_campaigns = db.query(Campaign).filter(Campaign.active == True).count()

        metrics = DashboardMetricsResponse(
            total_campaigns=total_campaigns,
            total_feedbacks=total_feedbacks,
            active_campaigns=active_campaigns
        )

        return jsonify(metrics.model_dump()), 200

# Create a new dashboard
@dashboard_bp.post("/dashboard", responses={201: DashboardResponse, 400: {"message": "Invalid data"}}, tags=[dashboard_tag])
def create_dashboard(body: DashboardCreate):
    """Create a new dashboard"""
    if not body.components or len(body.components) < 1:
        return jsonify({"message": "A dashboard must have at least one component."}), 400

    with SessionLocal() as db:
        try:
            campaigns = db.query(Campaign).filter(Campaign.id.in_(body.campaign_ids)).all()

            components = [
                Component(
                    name=component["name"],
                    description=component.get("description"),
                    active=component["active"],
                    type=ComponentType(component["type"].lower()),
                    settings=component.get("settings")
                )
                for component in body.components
            ]

            dashboard = Dashboard(name=body.name, description=body.description, campaigns=campaigns, components=components)
            db.add(dashboard)
            db.commit()
            return jsonify(
                DashboardResponse(
                    id=dashboard.id,
                    name=dashboard.name,
                    description=dashboard.description,
                    campaigns=[c.id for c in dashboard.campaigns],
                    components=[
                        {
                            "name": c.name,
                            "description": c.description,
                            "active": c.active,
                            "type": c.type.value,
                            "settings": c.settings
                        }
                        for c in dashboard.components
                    ]
                ).model_dump()
            ), 201
        except Exception as e:
            db.rollback()
            return jsonify({"message": str(e)}), 400

# Get a dashboard by ID
@dashboard_bp.get("/dashboard/<int:dashboard_id>", responses={200: DashboardResponse, 404: {"message": "Not found"}}, tags=[dashboard_tag])
def get_dashboard(path: DashboardIDParam):
    """Retrieve a dashboard by ID"""
    with SessionLocal() as db:
        dashboard = db.query(Dashboard).filter(Dashboard.id == path.dashboard_id).first()
        if not dashboard:
            return jsonify({"message": "Dashboard not found"}), 404
        return jsonify(
            DashboardResponse(
                id=dashboard.id,
                name=dashboard.name,
                description=dashboard.description,
                campaigns=[c.id for c in dashboard.campaigns],
                components=[
                    {
                        "name": c.name,
                        "description": c.description,
                        "active": c.active,
                        "type": c.type.value,
                        "settings": c.settings
                    }
                    for c in dashboard.components
                ]
            ).model_dump()
        ), 200

# Update a dashboard by ID
@dashboard_bp.put("/dashboard/<int:dashboard_id>", responses={200: DashboardResponse, 404: {"message": "Not found"}}, tags=[dashboard_tag])
def update_dashboard(path: DashboardIDParam, body: DashboardUpdate):
    """Update a dashboard"""
    with SessionLocal() as db:
        dashboard = db.query(Dashboard).filter(Dashboard.id == path.dashboard_id).first()
        if not dashboard:
            return jsonify({"message": "Dashboard not found"}), 404

        dashboard.name = body.name
        dashboard.description = body.description
        dashboard.campaigns = db.query(Campaign).filter(Campaign.id.in_(body.campaign_ids)).all()
        dashboard.components = [
            Component(
                name=component["name"],
                description=component.get("description"),
                active=component["active"],
                type=ComponentType(component["type"].lower()),
                settings=component.get("settings")
            )
            for component in body.components
        ]
        db.commit()
        return jsonify(
            DashboardResponse(
                id=dashboard.id,
                name=dashboard.name,
                description=dashboard.description,
                campaigns=[c.id for c in dashboard.campaigns],
                components=[
                    {
                        "name": c.name,
                        "description": c.description,
                        "active": c.active,
                        "type": c.type.value,
                        "settings": c.settings
                    }
                    for c in dashboard.components
                ]
            ).model_dump()
        ), 200

# Delete a dashboard by ID
@dashboard_bp.delete("/dashboard/<int:dashboard_id>", responses={200: {"message": "Dashboard deleted"}, 404: {"message": "Not found"}}, tags=[dashboard_tag])
def delete_dashboard(path: DashboardIDParam):
    """Delete a dashboard"""
    with SessionLocal() as db:
        dashboard = db.query(Dashboard).filter(Dashboard.id == path.dashboard_id).first()
        if not dashboard:
            return jsonify({"message": "Dashboard not found"}), 404

        db.delete(dashboard)
        db.commit()
        return jsonify({"message": "Dashboard deleted"}), 200

# List all dashboards
@dashboard_bp.get("/dashboards", responses={200: DashboardListResponse}, tags=[dashboard_tag])
def list_dashboards():
    """List all dashboards"""
    with SessionLocal() as db:
        dashboards = db.query(Dashboard).all()
        response = DashboardListResponse(
            items=[
                DashboardResponse(
                    id=d.id,
                    name=d.name,
                    description=d.description,
                    campaigns=[c.id for c in d.campaigns],
                    components=[
                        {
                            "name": c.name,
                            "description": c.description,
                            "active": c.active,
                            "type": c.type.value,
                            "settings": c.settings
                        }
                        for c in d.components
                    ]
                )
                for d in dashboards
            ],
            total=len(dashboards)
        )
        return jsonify(response.model_dump())