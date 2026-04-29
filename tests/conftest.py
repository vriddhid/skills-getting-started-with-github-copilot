"""Pytest configuration and shared fixtures for backend tests."""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def reset_activities():
    """
    Fixture that captures the initial state of activities before each test
    and restores it after the test completes.
    
    This prevents state contamination between tests since the app mutates
    the global activities dict when students sign up or unregister.
    """
    # Arrange: Capture the initial state
    original_activities = copy.deepcopy(activities)
    
    yield
    
    # Cleanup: Restore the original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Provide a TestClient for making HTTP requests to the FastAPI app."""
    return TestClient(app)
