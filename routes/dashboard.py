from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from config import SessionLocal
from model import Campaign, Feedback, Dashboard, Component, ComponentType, FeedbackAnalysis, SentimentCategory
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
from sqlalchemy import func, case

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
            x_axis = component.settings.get("x_axis", "sentiment_category")
            y_axis = component.settings.get("y_axis", "count")
            
            field_mapping = {
                "sentiment_category": FeedbackAnalysis.sentiment_category,
                "gender": Feedback.gender,
                "age_range": Feedback.age_range,
                "education_level": Feedback.education_level,
                "country": Feedback.country,
                "state": Feedback.state,
                "sentiment": FeedbackAnalysis.sentiment,
                "word_count": FeedbackAnalysis.word_count,
                "feedback_length": FeedbackAnalysis.feedback_length
            }
            
            x_field = field_mapping.get(x_axis, FeedbackAnalysis.sentiment_category)
            
            if y_axis == "count":
                y_expression = func.count().label('value')
            elif y_axis == "avg_sentiment":
                y_expression = func.avg(FeedbackAnalysis.sentiment).label('value')
            elif y_axis in field_mapping:
                y_field = field_mapping[y_axis]
                if y_axis in ["sentiment", "word_count", "feedback_length"]:
                    y_expression = func.avg(y_field).label('value')
                else:
                    y_expression = func.count().label('value')
            else:
                y_expression = func.count().label('value')

            chart_data = db.query(
                x_field.label('label'),
                y_expression
            ).join(
                Feedback, FeedbackAnalysis.feedback_id == Feedback.id
            ).filter(
                Feedback.campaign_id.in_(campaign_ids)
            ).group_by(x_field).all()

            if chart_data:
                labels = []
                values = []
                for row in chart_data:
                    if hasattr(row.label, 'value'):
                        labels.append(row.label.value)
                    else:
                        labels.append(str(row.label))
                    values.append(float(row.value) if row.value else 0)
                
                data_payload = {
                    "labels": labels,
                    "values": values
                }
            else:
                data_payload = {"data": {"message": "No chart data available"}}

        elif component.type.value == "word_cloud":
            feedbacks = db.query(Feedback.message).filter(Feedback.campaign_id.in_(campaign_ids)).all()
            word_count = {}
            stopwords = {
                "a", "o", "e", "de", "do", "da", "das", "dos", "em", "um", "uma", "uns", "umas", "para", "por", "com",
                "no", "na", "nos", "nas", "ao", "à", "aos", "às", "que", "se", "é", "não", "sim", "mas", "ou", "como",
                "the", "and", "of", "to", "in", "for", "on", "with", "at", "by", "an", "be", "is", "are", "was", "were",
                "it", "this", "that", "from", "as", "or", "if", "so", "do", "does", "did", "not"
            }
            for feedback in feedbacks:
                words = feedback.message.split()
                for word in words:
                    word = word.lower().strip(".,!?\"'()[]{}:;")
                    if word and word not in stopwords:
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
                    sentiment_summary[data.sentiment_category.value.lower()] += 1
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
            trend_data = db.query(
                func.date(Feedback.created_at).label('date'),
                func.count(FeedbackAnalysis.id).label('total_feedbacks'),
                func.avg(FeedbackAnalysis.sentiment).label('avg_sentiment'),
                func.sum(
                    case(
                        (FeedbackAnalysis.sentiment_category == SentimentCategory.POSITIVE, 1),
                        else_=0
                    )
                ).label('positive_count'),
                func.sum(
                    case(
                        (FeedbackAnalysis.sentiment_category == SentimentCategory.NEGATIVE, 1),
                        else_=0
                    )
                ).label('negative_count')
            ).join(
                Feedback, FeedbackAnalysis.feedback_id == Feedback.id
            ).filter(
                Feedback.campaign_id.in_(campaign_ids)
            ).group_by(
                func.date(Feedback.created_at)
            ).order_by(
                func.date(Feedback.created_at)
            ).all()

            if trend_data:
                labels = [row.date for row in trend_data]
                sentiment_scores = [float(row.avg_sentiment) for row in trend_data]
                
                satisfaction_trend = []
                for row in trend_data:
                    if row.total_feedbacks and row.total_feedbacks > 0:
                        satisfaction_rate = (row.positive_count / row.total_feedbacks) * 100
                        satisfaction_trend.append(round(satisfaction_rate, 2))
                    else:
                        satisfaction_trend.append(0)

                data_payload = {
                    "labels": labels,
                    "sentiment_scores": sentiment_scores,
                    "satisfaction_trend": satisfaction_trend,
                    "total_feedbacks": [int(row.total_feedbacks) for row in trend_data]
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