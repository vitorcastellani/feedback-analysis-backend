"""
Improvements for sentiment analysis in Portuguese
"""

# Dictionary of Portuguese words with sentiment scores
PORTUGUESE_SENTIMENT_DICT = {
    # Positive
    'excelente': 0.8, 'ótimo': 0.7, 'ótima': 0.7, 'maravilhoso': 0.9,
    'fantástico': 0.8, 'perfeito': 0.8, 'amei': 0.9, 'adorei': 0.8,
    'incrível': 0.8, 'sensacional': 0.8, 'show': 0.6, 'top': 0.6,
    'demais': 0.5, 'legal': 0.4, 'bacana': 0.4, 'massa': 0.5,
    'genial': 0.7, 'espetacular': 0.8, 'surpreendente': 0.6,
    'recomendo': 0.6, 'aprovado': 0.5, 'valeu': 0.4, 'curti': 0.5,
    
    # Negative  
    'péssimo': -0.8, 'horrível': -0.8, 'terrível': -0.8, 'ruim': -0.6,
    'odiei': -0.9, 'detestei': -0.8, 'nojento': -0.7, 'lixo': -0.7,
    'porcaria': -0.7, 'decepcionante': -0.6, 'frustrante': -0.6,
    'chato': -0.4, 'enjoativo': -0.5, 'cansativo': -0.4,
    'confuso': -0.3, 'complicado': -0.3, 'difícil': -0.2,
    
    # Neutral that can confuse
    'básico': 0.1, 'simples': 0.1, 'comum': 0.0, 'normal': 0.0,
    'regular': -0.1, 'mediano': -0.1, 'ok': 0.1, 'razoável': 0.0,
    
    # Intensifiers
    'muito': 0.3, 'super': 0.4, 'bem': 0.2, 'bastante': 0.2,
    'extremamente': 0.5, 'completamente': 0.3, 'totalmente': 0.3,
    'pouco': -0.2, 'meio': -0.1, 'mais_ou_menos': -0.1,
}

# Brazilian expressions and slang
BRAZILIAN_EXPRESSIONS = {
    'da hora': 0.6, 'maneiro': 0.5, 'irado': 0.6, 'massa': 0.5,
    'dahora': 0.6, 'tri': 0.5, 'bão': 0.4, 'daora': 0.5,
    'mó bom': 0.6, 'mo bom': 0.6, 'muito bom': 0.6,
    'nota 10': 0.8, 'nota dez': 0.8, '10': 0.6,
    'valeu a pena': 0.7, 'vale a pena': 0.7,
    'não prestou': -0.6, 'nao prestou': -0.6,
    'uma bosta': -0.8, 'uma merda': -0.8,
    'furada': -0.5, 'enrolação': -0.4,
}

# Corrections for words that get lost in translation
TRANSLATION_FIXES = {
    'curso incrível': 'incredible course',
    'muito bom': 'very good', 
    'péssimo curso': 'terrible course',
    'adorei o curso': 'loved the course',
    'odiei tudo': 'hated everything',
    'recomendo muito': 'highly recommend',
    'não recomendo': 'do not recommend',
    'vale a pena': 'worth it',
    'não vale a pena': 'not worth it',
    'perda de tempo': 'waste of time',
    'curso show': 'great course',
    'curso top': 'top course',
    'curso fraco': 'weak course',
    'curso ruim': 'bad course',
}

def get_portuguese_sentiment_boost(text: str) -> float:
    """
    Calculates sentiment boost based on Portuguese words
    """
    text_lower = text.lower()
    boost = 0.0
    word_count = 0
    
    # Check words from Portuguese dictionary
    for word, score in PORTUGUESE_SENTIMENT_DICT.items():
        if word in text_lower:
            boost += score
            word_count += 1
    
    # Check Brazilian expressions
    for expr, score in BRAZILIAN_EXPRESSIONS.items():
        if expr in text_lower:
            boost += score * 1.2  # Higher boost for expressions
            word_count += 1
    
    # Return average boost if words were found
    return boost / word_count if word_count > 0 else 0.0

def preprocess_portuguese_text(text: str) -> str:
    """
    Preprocesses Portuguese text before translation
    """
    text_lower = text.lower()
    
    # Apply translation corrections
    for pt_phrase, en_phrase in TRANSLATION_FIXES.items():
        if pt_phrase in text_lower:
            text = text.replace(pt_phrase, en_phrase)
    
    return text

def calibrate_portuguese_score(vader_score: float, original_text: str) -> float:
    """
    Calibrates VADER score for Portuguese
    """
    # Calculate boost based on Portuguese words
    pt_boost = get_portuguese_sentiment_boost(original_text)
    
    # Apply correction factor to compensate for translation loss
    calibrated_score = vader_score * 1.3  # Factor based on analysis (0.795/0.315 ≈ 2.5, using conservative 1.3)
    
    # Add Portuguese words boost
    calibrated_score += pt_boost
    
    # Ensure it stays in range [-1, 1]
    calibrated_score = max(-1.0, min(1.0, calibrated_score))
    
    return calibrated_score

def adjust_thresholds_for_portuguese() -> tuple:
    """
    Returns adjusted thresholds for Portuguese
    """
    # Lower thresholds to compensate for lower scores
    positive_threshold = 0.03  # instead of 0.05
    negative_threshold = -0.03  # instead of -0.05
    
    return positive_threshold, negative_threshold
