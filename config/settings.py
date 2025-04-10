import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Settings for the text analysis
SHORT_SENTENCE_BOOST = float(os.getenv("SHORT_SENTENCE_BOOST", 0.2))
SHORT_SENTENCE_THRESHOLD = int(os.getenv("SHORT_SENTENCE_THRESHOLD", 5))
NEUTRAL_PENALTY_THRESHOLD = int(os.getenv("NEUTRAL_PENALTY_THRESHOLD", 50))
NEUTRAL_PENALTY_FACTOR = float(os.getenv("NEUTRAL_PENALTY_FACTOR", 0.9))
