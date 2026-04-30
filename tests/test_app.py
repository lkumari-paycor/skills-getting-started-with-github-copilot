import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    # Arrange: (No setup needed for this test)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Act: Sign up
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: Sign up
    assert signup_response.status_code in (200, 400)  # 400 if already signed up

    # Act: Unregister
    unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")

    # Assert: Unregister
    assert unregister_response.status_code in (200, 400)  # 400 if not signed up
