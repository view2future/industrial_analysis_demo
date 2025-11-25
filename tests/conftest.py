import pytest
from app import app as flask_app_instance
from app import init_db
from src.routes.streaming_routes import streaming_bp
import os

@pytest.fixture
def app():
    flask_app_instance.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "LOGIN_DISABLED": True # Disable login for testing
    })
    
    # Register the blueprint within the test app context
    flask_app_instance.register_blueprint(streaming_bp, url_prefix='/streaming')

    # Initialize the database for the test app
    with flask_app_instance.app_context():
        init_db()

    yield flask_app_instance

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()