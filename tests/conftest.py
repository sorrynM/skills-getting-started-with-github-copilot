"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture that provides sample activities for testing.
    """
    return {
        "Test Activity": {
            "description": "A test activity",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 10,
            "participants": ["alice@test.edu", "bob@test.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Wednesdays, 2:00 PM - 3:00 PM",
            "max_participants": 5,
            "participants": []
        }
    }


@pytest.fixture
def setup_activities(sample_activities):
    """
    Fixture that resets the activities to a known state before each test.
    This ensures test isolation by clearing and restoring activities.
    """
    # Arrange: Clear existing activities and add test data
    activities.clear()
    activities.update(sample_activities)
    
    yield  # Test runs here
    
    # Cleanup: Clear activities after test
    activities.clear()
