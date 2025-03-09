import re
from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from sqlalchemy.orm import Session
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from model import Feedback, FeedbackAnalysis, SentimentCategory
from schemas import FeedbackAnalysisResponse, FeedbackAnalysisCreate
from config import SessionLocal, SHORT_SENTENCE_BOOST, SHORT_SENTENCE_THRESHOLD, NEUTRAL_PENALTY_THRESHOLD, NEUTRAL_PENALTY_FACTOR

# Create a new Tag
feedback_analysis_tag = Tag(name="Feedback Analysis", description="Operations related to feedback sentiment analysis.")

# Create a new Blueprint
feedback_analysis_bp = APIBlueprint('feedback_analysis', __name__)

# Initialize the sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Ensure deterministic results for langdetect
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Tries to detect the language, but assumes Portuguese if detection is unreliable."""
    try:
        detected_lang = detect(text)
        if detected_lang not in ["en", "pt", "es", "fr", "de"]:
            return "pt"
        return detected_lang
    except:
        return "pt"

def analyze_sentiment(text: str):
    """Detects language, translates if needed, and applies sentiment analysis."""

    feedback_length = len(text)
    word_count = len(text.split())

    try:
        lang = detect(text)
    except:
        lang = "pt"

    if lang != "en":
        text = GoogleTranslator(source=lang, target="en").translate(text)

    sentences = re.split(r"[.!?]", text)
    compound_scores = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentiment = analyzer.polarity_scores(sentence)
        compound = sentiment["compound"]
        sentence_word_count = len(sentence.split())

        # Boost short emotional sentences
        if sentence_word_count <= SHORT_SENTENCE_THRESHOLD:
            if sentiment["pos"] > 0.5:
                compound += SHORT_SENTENCE_BOOST
            elif sentiment["neg"] > 0.5:
                compound -= SHORT_SENTENCE_BOOST

        # Penalize long texts that are too neutral
        if sentiment["neu"] > 0.7 and sentence_word_count > NEUTRAL_PENALTY_THRESHOLD:
            compound -= NEUTRAL_PENALTY_FACTOR

        compound_scores.append(compound)

    final_compound = sum(compound_scores) / len(compound_scores) if compound_scores else 0.0

    # Determine sentiment category
    if final_compound >= 0.05:
        sentiment_category = SentimentCategory.POSITIVE.value
    elif final_compound <= -0.05:
        sentiment_category = SentimentCategory.NEGATIVE.value
    else:
        sentiment_category = SentimentCategory.NEUTRAL.value

    return final_compound, sentiment_category, lang, word_count, feedback_length

def get_star_rating(sentiment_score: float) -> int:
    """Converts sentiment score (-1 to 1) into a 1-5 star rating with better scaling."""
    
    if sentiment_score >= 0.7:
        return 5
    elif sentiment_score <= -0.6:
        return 1
    else:
        return round((sentiment_score + 1) * 2.5)

@feedback_analysis_bp.post("/feedback/analyze", responses={201: FeedbackAnalysisResponse, 404: {"message": "Feedback not found"}}, tags=[feedback_analysis_tag])
def analyze_feedback(body: FeedbackAnalysisCreate):
    """Analyze sentiment of a feedback message in multiple languages and store it."""

    db: Session = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == body.feedback_id).first()

    if not feedback:
        db.close()
        return jsonify({"message": "Feedback not found"}), 404

    # Check if already analyzed
    existing_analysis = db.query(FeedbackAnalysis).filter(FeedbackAnalysis.feedback_id == body.feedback_id).first()
    if existing_analysis:
        db.close()
        return jsonify(FeedbackAnalysisResponse.model_validate(existing_analysis.__dict__).model_dump()), 200

    # Perform sentiment analysis
    sentiment_score, sentiment_category, detected_language, word_count, feedback_length = analyze_sentiment(feedback.message)
    star_rating = get_star_rating(sentiment_score)

    new_analysis = FeedbackAnalysis(
        feedback_id=body.feedback_id,
        sentiment=sentiment_score,
        sentiment_category=sentiment_category,
        star_rating=star_rating,
        detected_language=detected_language,
        word_count=word_count,
        feedback_length=feedback_length
    )
    
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    response = FeedbackAnalysisResponse.model_validate(new_analysis.__dict__).model_dump()

    db.close()
    return jsonify(response), 201