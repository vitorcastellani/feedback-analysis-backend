from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from config import SessionLocal
from model import Campaign, Feedback
from schemas import DashboardMetricsResponse

# Create a new Tag
dashboard_tag = Tag(name="Dashboard", description="Operations related to system dashboards.")

# Create a new Blueprint
dashboard_bp = APIBlueprint('dashboard', __name__)

@dashboard_bp.get("/dashboard-metrics", responses={200: DashboardMetricsResponse}, tags=[dashboard_tag])
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