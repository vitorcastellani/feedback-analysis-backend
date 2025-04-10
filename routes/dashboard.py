from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from config import SessionLocal
from model import Campaign, Feedback, Dashboard, Component, ComponentType, FeedbackAnalysis
from schemas import (
    DashboardMetricsResponse,
    DashboardIDParam,
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardListResponse,
    DashboardComponentIDParam,
    DashboardComponentResponse,
)

# Create a new Tag for the Dashboard module
dashboard_tag = Tag(name="Dashboard", description="Operations related to dashboards.")

# Create a new API Blueprint for dashboard routes
dashboard_bp = APIBlueprint("dashboard", __name__)

# Route: Get system metrics for the dashboard
@dashboard_bp.get(
    "/dashboard-system-metrics",
    responses={200: DashboardMetricsResponse},
    tags=[dashboard_tag],
)
def get_dashboard_metrics():
    """Retrieve system metrics for the dashboard."""
    with SessionLocal() as db:
        total_campaigns = db.query(Campaign).count()
        total_feedbacks = db.query(Feedback).count()
        active_campaigns = db.query(Campaign).filter(Campaign.active == True).count()

        metrics = DashboardMetricsResponse(
            total_campaigns=total_campaigns,
            total_feedbacks=total_feedbacks,
            active_campaigns=active_campaigns,
        )

        return jsonify(metrics.model_dump()), 200


# Route: Create a new dashboard
@dashboard_bp.post(
    "/dashboard",
    responses={201: DashboardResponse, 400: {"message": "Invalid data"}},
    tags=[dashboard_tag],
)
def create_dashboard(body: DashboardCreate):
    """Create a new dashboard."""
    if not body.components or len(body.components) < 1:
        return jsonify({"message": "A dashboard must have at least one component."}), 400

    with SessionLocal() as db:
        try:
            # Fetch campaigns associated with the dashboard
            campaigns = db.query(Campaign).filter(Campaign.id.in_(body.campaign_ids)).all()

            # Create components for the dashboard
            components = [
                Component(
                    name=component["name"],
                    description=component.get("description"),
                    type=ComponentType(component["type"].lower()),
                    settings=component.get("settings"),
                )
                for component in body.components
            ]

            # Create and save the dashboard
            dashboard = Dashboard(
                name=body.name,
                description=body.description,
                campaigns=campaigns,
                components=components,
            )
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
                            "type": c.type.value,
                            "settings": c.settings,
                        }
                        for c in dashboard.components
                    ],
                ).model_dump()
            ), 201
        except Exception as e:
            db.rollback()
            return jsonify({"message": str(e)}), 400


# Route: Get a dashboard by ID
@dashboard_bp.get(
    "/dashboard/<int:dashboard_id>",
    responses={200: DashboardResponse, 404: {"message": "Not found"}},
    tags=[dashboard_tag],
)
def get_dashboard(path: DashboardIDParam):
    """Retrieve a dashboard by its ID."""
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
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "type": c.type.value,
                        "settings": c.settings,
                    }
                    for c in dashboard.components
                ],
            ).model_dump()
        ), 200


# Route: Update a dashboard by ID
@dashboard_bp.put(
    "/dashboard/<int:dashboard_id>",
    responses={200: DashboardResponse, 404: {"message": "Not found"}},
    tags=[dashboard_tag],
)
def update_dashboard(path: DashboardIDParam, body: DashboardUpdate):
    """Update an existing dashboard."""
    with SessionLocal() as db:
        dashboard = db.query(Dashboard).filter(Dashboard.id == path.dashboard_id).first()
        if not dashboard:
            return jsonify({"message": "Dashboard not found"}), 404

        # Update dashboard properties
        dashboard.name = body.name
        dashboard.description = body.description
        dashboard.campaigns = db.query(Campaign).filter(Campaign.id.in_(body.campaign_ids)).all()
        dashboard.components = [
            Component(
                name=component["name"],
                description=component.get("description"),
                type=ComponentType(component["type"].lower()),
                settings=component.get("settings"),
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
                        "type": c.type.value,
                        "settings": c.settings,
                    }
                    for c in dashboard.components
                ],
            ).model_dump()
        ), 200


# Route: Delete a dashboard by ID
@dashboard_bp.delete(
    "/dashboard/<int:dashboard_id>",
    responses={200: {"message": "Dashboard deleted"}, 404: {"message": "Not found"}},
    tags=[dashboard_tag],
)
def delete_dashboard(path: DashboardIDParam):
    """Delete a dashboard by its ID."""
    with SessionLocal() as db:
        dashboard = db.query(Dashboard).filter(Dashboard.id == path.dashboard_id).first()
        if not dashboard:
            return jsonify({"message": "Dashboard not found"}), 404

        db.delete(dashboard)
        db.commit()
        return jsonify({"message": "Dashboard deleted"}), 200


# Route: List all dashboards
@dashboard_bp.get(
    "/dashboards",
    responses={200: DashboardListResponse},
    tags=[dashboard_tag],
)
def list_dashboards():
    """List all dashboards."""
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
                            "type": c.type.value,
                            "settings": c.settings,
                        }
                        for c in d.components
                    ],
                )
                for d in dashboards
            ],
            total=len(dashboards),
        )
        return jsonify(response.model_dump())


# Route: Get data for a specific component in a dashboard
@dashboard_bp.get(
    "/dashboard/<int:dashboard_id>/component/<int:component_id>/data",
    responses={
        200: DashboardComponentResponse,
        404: {"message": "Not found"},
        400: {"message": "Invalid data"},
    },
    tags=[dashboard_tag],
)
def get_component_data(path: DashboardComponentIDParam):
    """Retrieve data for a specific component in a dashboard."""
    with SessionLocal() as db:
        # Validate the dashboard
        dashboard = db.query(Dashboard).filter(Dashboard.id == path.dashboard_id).first()
        if not dashboard:
            return jsonify({"message": "Dashboard not found"}), 404

        # Validate the component and ensure it belongs to the dashboard
        component = db.query(Component).filter(
            Component.id == path.component_id,
            Component.dashboard_id == path.dashboard_id,
        ).first()
        if not component:
            return jsonify({"message": "Component not found or does not belong to the specified dashboard"}), 404

        campaign_ids = [campaign.id for campaign in dashboard.campaigns]

        # Handle different component types
        if component.type.value in ["bar_chart", "line_chart", "pie_chart"]:
            x_axis = component.settings.get("x_axis")
            y_axis = component.settings.get("y_axis")

            if not x_axis or not y_axis:
                return jsonify({"message": "Both x_axis and y_axis must be specified in the component settings"}), 400

            try:
                if hasattr(FeedbackAnalysis, x_axis) and hasattr(FeedbackAnalysis, y_axis):
                    data = db.query(getattr(FeedbackAnalysis, x_axis), getattr(FeedbackAnalysis, y_axis)).filter(
                        FeedbackAnalysis.feedback_id.in_(
                            db.query(Feedback.id).filter(Feedback.campaign_id.in_(campaign_ids))
                        )
                    ).all()
                else:
                    data = db.query(getattr(Feedback, x_axis), getattr(Feedback, y_axis)).filter(
                        Feedback.campaign_id.in_(campaign_ids)
                    ).all()

                # Group by x_axis and calculate the average for y_axis
                grouped_data = {}
                for row in data:
                    x_value = str(getattr(row, x_axis))
                    y_value = getattr(row, y_axis)
                    if x_value not in grouped_data:
                        grouped_data[x_value] = {"sum": y_value, "count": 1}
                    else:
                        grouped_data[x_value]["sum"] += y_value
                        grouped_data[x_value]["count"] += 1

                data_payload = {
                    "labels": list(grouped_data.keys()),
                    "values": [group["sum"] / group["count"] for group in grouped_data.values()],
                }
            except AttributeError:
                return jsonify({"message": f"Invalid x_axis or y_axis configuration: {x_axis}, {y_axis}"}), 400

        elif component.type.value == "word_cloud":
            feedbacks = db.query(Feedback.message).filter(Feedback.campaign_id.in_(campaign_ids)).all()
            word_count = {}
            for feedback in feedbacks:
                words = feedback.message.split()
                for word in words:
                    word = word.lower()
                    word_count[word] = word_count.get(word, 0) + 1
            data_payload = {
                "words": [[word, count] for word, count in word_count.items()]
            }

        elif component.type.value == "sentiment_analysis":
            sentiment_data = db.query(FeedbackAnalysis).filter(FeedbackAnalysis.feedback_id.in_(
                db.query(Feedback.id).filter(Feedback.campaign_id.in_(campaign_ids))
            )).all()
            if sentiment_data:
                sentiment_summary = {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                }
                total_sentiment_score = 0

                for data in sentiment_data:
                    sentiment_summary[data.sentiment_category.lower()] += 1
                    total_sentiment_score += data.sentiment

                total_sentiments = sum(sentiment_summary.values())
                data_payload = {
                    "sentiment": total_sentiment_score / len(sentiment_data),
                    "positive_score": sentiment_summary["positive"] / total_sentiments,
                    "neutral_score": sentiment_summary["neutral"] / total_sentiments,
                    "negative_score": sentiment_summary["negative"] / total_sentiments,
                }
            else:
                data_payload = {"data": {"message": "No sentiment data available"}}

        elif component.type.value == "trend_analysis":
            trend_data = db.query(FeedbackAnalysis.sentiment, Feedback.created_at).join(
                Feedback, FeedbackAnalysis.feedback_id == Feedback.id
            ).filter(
                Feedback.campaign_id.in_(campaign_ids)
            ).order_by(Feedback.created_at).all()

            if trend_data:
                data_payload = {
                    "labels": [row.created_at.strftime("%Y-%m-%d") for row in trend_data],
                    "values": [row.sentiment for row in trend_data],
                }
            else:
                data_payload = {"data": {"message": "No trend data available"}}

        else:
            data_payload = {"message": "Component type not mapped"}

        response_data = DashboardComponentResponse(
            id=component.id,
            name=component.name,
            type=component.type.value,
            settings=component.settings or {},
            data=data_payload,
        )
        return jsonify(response_data.model_dump()), 200