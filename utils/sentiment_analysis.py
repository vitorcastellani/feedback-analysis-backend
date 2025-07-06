import re
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import (
    SHORT_SENTENCE_BOOST,
    SHORT_SENTENCE_THRESHOLD,
    NEUTRAL_PENALTY_THRESHOLD,
    NEUTRAL_PENALTY_FACTOR,
)
from model.enums import SentimentCategory
from utils.portuguese_sentiment import (
    preprocess_portuguese_text,
    calibrate_portuguese_score,
    adjust_thresholds_for_portuguese
)

# Initialize the sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Ensure deterministic results for langdetect
DetectorFactory.seed = 0


def detect_language(text: str) -> str:
    """
    Detects the language of the given text.

    Args:
        text (str): The input text.

    Returns:
        str: The detected language code (e.g., 'en', 'pt').
    """
    try:
        detected_lang = detect(text)
        return detected_lang if detected_lang in ["en", "pt", "es", "fr", "de"] else "pt"
    except Exception:
        return "pt"


def analyze_sentiment(text: str):
    """
    Analyzes the sentiment of a given text with improvements for Portuguese.

    Args:
        text (str): The input text.

    Returns:
        tuple: A tuple containing:
            - final_compound (float): The overall sentiment score (-1 to 1).
            - sentiment_category (str): The sentiment category ('positive', 'negative', 'neutral').
            - lang (str): The detected language of the text.
            - word_count (int): The number of words in the text.
            - feedback_length (int): The length of the text in characters.
    """
    feedback_length = len(text)
    word_count = len(text.split())
    original_text = text

    # Detect the language of the text
    lang = detect_language(text)

    # Preprocess Portuguese text if detected
    if lang == "pt":
        text = preprocess_portuguese_text(text)

    # Translate text to English if not already in English
    if lang != "en":
        text = GoogleTranslator(source=lang, target="en").translate(text)

    # Split text into sentences
    sentences = re.split(r"[.!?]", text)
    compound_scores = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Analyze sentiment of the sentence
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

    # Calculate the final compound score
    final_compound = sum(compound_scores) / len(compound_scores) if compound_scores else 0.0

    # Adjust the final compound score for Portuguese texts
    if lang == "pt":
        final_compound = calibrate_portuguese_score(final_compound, original_text)
        positive_threshold, negative_threshold = adjust_thresholds_for_portuguese()
    else:
        positive_threshold, negative_threshold = 0.05, -0.05

    # Determine sentiment category with adjusted thresholds
    if final_compound >= positive_threshold:
        sentiment_category = SentimentCategory.POSITIVE
    elif final_compound <= negative_threshold:
        sentiment_category = SentimentCategory.NEGATIVE
    else:
        sentiment_category = SentimentCategory.NEUTRAL

    return final_compound, sentiment_category, lang, word_count, feedback_length


def get_star_rating(sentiment_score: float) -> int:
    """
    Converts a sentiment score (-1 to 1) into a 1-5 star rating.

    Args:
        sentiment_score (float): The sentiment score.

    Returns:
        int: The corresponding star rating (1 to 5).
    """
    if sentiment_score >= 0.7:
        return 5
    elif sentiment_score <= -0.6:
        return 1
    return round((sentiment_score + 1) * 2.5)