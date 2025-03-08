import os
from dotenv import load_dotenv
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from model.base import Base

# Set TESTING=false if not set
if "TESTING" not in os.environ:
    os.environ["TESTING"] = "false"

# Load environment variables
load_dotenv()

# Detect if running in test mode
IS_TESTING = os.getenv("TESTING", "false").lower() == "true"

# Select the correct database
DB_PATH = os.getenv("DB_PATH", "database/")
DB_NAME = os.getenv("DB_TEST_NAME") if IS_TESTING else os.getenv("DB_PRODUCTION_NAME")

# Ensure database directory exists
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# Database URL
DB_URL = f"sqlite:///{DB_PATH}{DB_NAME}"

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create a session factory
SessionLocal = scoped_session(sessionmaker(bind=engine))

# Ensure the database is created
if not database_exists(engine.url):
    create_database(engine.url)

# Ensure all tables are created
Base.metadata.create_all(engine)