import os

# Set TESTING=true if not set
os.environ["TESTING"] = "true"

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from routes.feedback import feedback_bp
from config.db import Base

# Use the test database
TEST_DATABASE_URL = f"sqlite:///database/{os.getenv('DB_TEST_NAME', 'test.sqlite')}"

# Create a single database engine for tests
test_engine = create_engine(TEST_DATABASE_URL)

# Ensure all tables are created
Base.metadata.create_all(test_engine)

# Create a test session factory
TestingSessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=test_engine))

@pytest.fixture(scope="session")
def test_session():
    """Provides a test database session using the correct engine."""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def app(test_session):
    """Creates a Flask test app using the test database session."""
    app = Flask(__name__)
    app.register_blueprint(feedback_bp)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """Provides a test client for API requests."""
    return app.test_client()

@pytest.fixture
def db_session(test_session):
    """Ensures API and tests use the same session."""
    yield test_session
    test_session.rollback()
