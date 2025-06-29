from model import Feedback, SentimentCategory, Campaign
from model.enums import AgeRange, Gender, EducationLevel, Country, State
from services import feedback_queue, processing_feedbacks

def test_analyze_feedback_success(client, db_session):
    """Test successful sentiment analysis for an existing feedback."""
    campaign = Campaign(
        name="Analysis Campaign",
        description="Campaign for feedback analysis test",
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    feedback = Feedback(
        message="Amei a música, foi incrível!",
        campaign_id=campaign.id,
        age_range=AgeRange.other.value,
        gender=Gender.prefer_not_to_say.value,
        education_level=EducationLevel.other.value,
        country=Country.other.value,
        state=State.other.value,
        user_ip=None,
        user_agent=None
    )
    db_session.add(feedback)
    db_session.commit()

    response = client.post("/api/feedback/analyze", json={"feedback_id": feedback.id})
    assert response.status_code == 201
    data = response.get_json()

    assert "feedback_id" in data
    assert "sentiment" in data
    assert "sentiment_category" in data
    assert "star_rating" in data
    assert "detected_language" in data
    assert "word_count" in data
    assert "feedback_length" in data

    assert data["sentiment_category"] in [
        SentimentCategory.POSITIVE.value,
        SentimentCategory.NEUTRAL.value,
        SentimentCategory.NEGATIVE.value
    ]
    assert data["feedback_id"] == feedback.id


def test_analyze_feedback_already_exists(client, db_session):
    """Test that analyzing the same feedback again returns the existing result."""
    campaign = Campaign(
        name="Duplicate Analysis Campaign",
        description="Campaign for duplicate analysis test",
        short_code="TEST"
    )
    db_session.add(campaign)
    db_session.commit()

    feedback = Feedback(
        message="Muito ruim, odiei essa experiência.",
        campaign_id=campaign.id,
        age_range=AgeRange.other.value,
        gender=Gender.prefer_not_to_say.value,
        education_level=EducationLevel.other.value,
        country=Country.other.value,
        state=State.other.value,
        user_ip=None,
        user_agent=None
    )
    db_session.add(feedback)
    db_session.commit()

    response1 = client.post("/api/feedback/analyze", json={"feedback_id": feedback.id})
    assert response1.status_code == 201
    data1 = response1.get_json()

    response2 = client.post("/api/feedback/analyze", json={"feedback_id": feedback.id})
    assert response2.status_code == 200
    data2 = response2.get_json()

    assert data1 == data2


def test_analyze_feedback_not_found(client):
    """Test analyzing a feedback that does not exist."""
    response = client.post("/api/feedback/analyze", json={"feedback_id": 9999})
    assert response.status_code == 404
    data = response.get_json()

    assert "message" in data
    assert data["message"] == "Feedback not found"


def test_analyze_all_feedbacks_success(client, db_session):
    """Test analyzing all feedbacks for specific campaigns."""
    campaign1 = Campaign(
        name="Campaign 1",
        description="First campaign",
        short_code="CAMP1"
    )
    campaign2 = Campaign(
        name="Campaign 2",
        description="Second campaign",
        short_code="CAMP2"
    )
    db_session.add_all([campaign1, campaign2])
    db_session.commit()

    feedback1 = Feedback(
        message="Ótimo produto!",
        campaign_id=campaign1.id,
        age_range=AgeRange.other.value,
        gender=Gender.prefer_not_to_say.value,
        education_level=EducationLevel.other.value,
        country=Country.other.value,
        state=State.other.value,
        user_ip=None,
        user_agent=None
    )
    feedback2 = Feedback(
        message="Não gostei do atendimento.",
        campaign_id=campaign1.id,
        age_range=AgeRange.other.value,
        gender=Gender.prefer_not_to_say.value,
        education_level=EducationLevel.other.value,
        country=Country.other.value,
        state=State.other.value,
        user_ip=None,
        user_agent=None
    )
    feedback3 = Feedback(
        message="Excelente qualidade!",
        campaign_id=campaign2.id,
        age_range=AgeRange.other.value,
        gender=Gender.prefer_not_to_say.value,
        education_level=EducationLevel.other.value,
        country=Country.other.value,
        state=State.other.value,
        user_ip=None,
        user_agent=None
    )
    db_session.add_all([feedback1, feedback2, feedback3])
    db_session.commit()

    response = client.post(
        "/api/feedback/analyze-all",
        json={"campaign_ids": [campaign1.id, campaign2.id]}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert "message" in data
    assert "Added" in data["message"]

    queue_size = len(list(feedback_queue.queue))
    assert queue_size == 3  # All feedbacks should be added to the queue


def test_analyze_all_feedbacks_no_campaign_ids(client):
    """Test analyzing all feedbacks without providing campaign IDs."""
    response = client.post("/api/feedback/analyze-all", json={"campaign_ids": []})
    assert response.status_code == 400
    data = response.get_json()

    assert "message" in data
    assert data["message"] == "Campaign IDs are required"


def test_analyze_all_feedbacks_no_feedbacks_to_analyze(client, db_session):
    """Test analyzing all feedbacks when no feedbacks are available for the campaigns."""
    campaign = Campaign(
        name="Empty Campaign",
        description="No feedbacks in this campaign",
        short_code="EMPTY"
    )
    db_session.add(campaign)
    db_session.commit()

    response = client.post(
        "/api/feedback/analyze-all",
        json={"campaign_ids": [campaign.id]}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert "message" in data
    assert data["message"] == "No feedbacks to analyze for the given campaigns"


def test_get_feedback_progress(client):
    """Test retrieving the progress of the feedback analysis queue."""
    feedback_queue.put(1)
    feedback_queue.put(2)
    feedback_queue.get()  # Remove one item from the queue
    processing_feedbacks.add(1)  # Add the removed item to processing

    response = client.get("/api/feedback/progress")
    assert response.status_code == 200
    data = response.get_json()

    assert "queue_size" in data
    assert "processing" in data
    assert data["queue_size"] == len(list(feedback_queue.queue))
    assert data["processing"] == len(processing_feedbacks)
