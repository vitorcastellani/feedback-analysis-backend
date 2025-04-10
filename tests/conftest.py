import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from routes import feedback_bp, feedback_analysis_bp, campaign_bp, dashboard_bp
from config import BaseModel, DB_URL

# Define the database file path for testing
TEST_DB_FILE = DB_URL.replace("sqlite:///", "")

# Create a new database engine for testing
test_engine = create_engine(DB_URL)

# Create a scoped session factory for testing
TestingSessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
)

@pytest.fixture(scope="session")
def setup_database():
    """
    Fixture to set up the database for the test session.
    Ensures a clean test database before the test session starts.
    """
    # Create all tables in the test database
    BaseModel.metadata.create_all(bind=test_engine)

    # Yield control to the test session
    yield

    # Remove any active session
    TestingSessionLocal.remove()

    # Dispose of the database engine
    test_engine.dispose()

@pytest.fixture
def db_session(setup_database):
    """
    Fixture to provide a new database session for each test.
    Resets the database by dropping and recreating all tables before each test.
    """
    # Drop and recreate all tables before each test
    BaseModel.metadata.drop_all(bind=test_engine)
    BaseModel.metadata.create_all(bind=test_engine)

    # Create a new session
    session = TestingSessionLocal()

    # Yield the session to the test
    yield session

    # Close the session after the test
    session.close()

@pytest.fixture
def app():
    """
    Fixture to create a Flask test application.
    Registers all blueprints and configures the app for testing.
    """
    app = Flask(__name__)
    app.register_blueprint(campaign_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(feedback_analysis_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """
    Fixture to provide a test client for making API requests.
    """
    return app.test_client()
