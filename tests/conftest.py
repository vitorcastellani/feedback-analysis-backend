import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from routes import feedback_bp, feedback_analysis_bp, campaign_bp, dashboard_bp
from config import BaseModel, DB_URL, SessionLocal

# Define the database file path
TEST_DB_FILE = DB_URL.replace("sqlite:///", "")

# Create a new database engine for testing
test_engine = create_engine(DB_URL)

# Create a test session factory
TestingSessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=test_engine))

@pytest.fixture(scope="session")
def setup_database():
    """Ensures a clean test database before the test session starts."""
    # Create a fresh database
    BaseModel.metadata.create_all(bind=test_engine)

    # Runs all tests
    yield

    # Close any active session
    TestingSessionLocal.remove()

    # Fully disconnect the database
    test_engine.dispose()

@pytest.fixture
def db_session(setup_database):
    """Creates a new database session and resets the database before each test."""
    
    # Drop and recreate all tables before each test
    BaseModel.metadata.drop_all(bind=test_engine)
    BaseModel.metadata.create_all(bind=test_engine)

    # Provide the test session to the test
    session = TestingSessionLocal()

    # Run the test
    yield session

    # Close the session after the test
    session.close()

@pytest.fixture
def app():
    """Creates a Flask test app using the test database session."""
    app = Flask(__name__)
    app.register_blueprint(campaign_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(feedback_analysis_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """Provides a test client for API requests."""
    return app.test_client()
