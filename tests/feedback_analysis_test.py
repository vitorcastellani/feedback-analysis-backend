from model import Feedback, SentimentCategory, Campaign

def test_analyze_feedback_success(client, db_session):
    """Test sentiment analysis for an existing feedback."""
    
    # Create a campaign entry
    campaign = Campaign(name="Analysis Campaign", description="Campaign for feedback analysis test")
    db_session.add(campaign)
    db_session.commit()
    
    # Create a feedback entry linked to the campaign
    feedback = Feedback(message="Amei a música, foi incrível!", campaign_id=campaign.id)
    db_session.add(feedback)
    db_session.commit()

    # Analyze the feedback
    response = client.post("/api/feedback/analyze", json={"feedback_id": feedback.id})
    assert response.status_code == 201
    data = response.get_json()

    # Validate response structure
    assert "feedback_id" in data
    assert "sentiment" in data
    assert "sentiment_category" in data
    assert "star_rating" in data
    assert "detected_language" in data
    assert "word_count" in data
    assert "feedback_length" in data

    # Ensure sentiment category is correctly determined
    assert data["sentiment_category"] in [SentimentCategory.POSITIVE.value, SentimentCategory.NEUTRAL.value, SentimentCategory.NEGATIVE.value]
    assert data["feedback_id"] == feedback.id


def test_analyze_feedback_already_exists(client, db_session):
    """Test that analyzing the same feedback again returns the existing result."""
    
    # Create a campaign entry
    campaign = Campaign(name="Duplicate Analysis Campaign", description="Campaign for duplicate analysis test")
    db_session.add(campaign)
    db_session.commit()
    
    # Create a feedback entry linked to the campaign
    feedback = Feedback(message="Muito ruim, odiei essa experiência.", campaign_id=campaign.id)
    db_session.add(feedback)
    db_session.commit()

    # Perform initial analysis
    response1 = client.post("/api/feedback/analyze", json={"feedback_id": feedback.id})
    assert response1.status_code == 201
    data1 = response1.get_json()

    # Perform the same analysis again
    response2 = client.post("/api/feedback/analyze", json={"feedback_id": feedback.id})
    assert response2.status_code == 200
    data2 = response2.get_json()

    # Ensure the result is the same
    assert data1 == data2


def test_analyze_feedback_not_found(client):
    """Test analyzing a feedback that does not exist."""
    
    response = client.post("/api/feedback/analyze", json={"feedback_id": 9999})
    assert response.status_code == 404
    data = response.get_json()

    assert "message" in data
    assert data["message"] == "Feedback not found"
