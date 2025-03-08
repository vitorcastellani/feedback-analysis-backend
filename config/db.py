import os
import sys
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from model.base import Base

# Load environment variables but DO NOT override existing ones
load_dotenv(override=False)

# Automatically detect if running tests
IS_TESTING = "pytest" in sys.argv[0]

# Select the correct database
DB_PATH = os.getenv("DB_PATH", "database/")
DB_NAME = "test.sqlite" if IS_TESTING else os.getenv("DB_PRODUCTION_NAME", "production.sqlite")

# Ensure database directory exists
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# Database URL
DB_URL = f"sqlite:///{DB_PATH}{DB_NAME}"

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create a session factory
SessionLocal = scoped_session(sessionmaker(bind=engine))

# Ensure all tables are created
Base.metadata.create_all(engine)