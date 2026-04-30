"""
Comprehensive unit tests for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activity participants to initial state before each test."""
    original_participants = {
        name: list(data["participants"]) for name, data in activities.items()
    }
    yield
    for name, data in activities.items():
        data["participants"] = original_participants[name]


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    """All activities should be returned."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_contains_expected_fields():
    """Each activity should contain description, schedule, max_participants, and participants."""
    response = client.get("/activities")
    assert response.status_code == 200
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    """A valid student should be signed up successfully."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    """Signing up for a non-existent activity should return 404."""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_adds_participant_to_list():
    """After signup the student's email should appear in the participants list."""
    email = "test@mergington.edu"
    signup_response = client.post("/activities/Programming Class/signup", params={"email": email})
    assert signup_response.status_code == 200
    response = client.get("/activities")
    participants = response.json()["Programming Class"]["participants"]
    assert email in participants


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/unregister
# ---------------------------------------------------------------------------

def test_unregister_success():
    """An already-registered student should be successfully removed."""
    # michael@mergington.edu is in Chess Club by default
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 200
    assert "michael@mergington.edu" in response.json()["message"]
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    """Unregistering from a non-existent activity should return 404."""
    response = client.post(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_registered():
    """Unregistering a student who is not in the activity should return 400."""
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered for this activity"


# ---------------------------------------------------------------------------
# GET /  (redirect)
# ---------------------------------------------------------------------------

def test_root_redirects_to_static():
    """GET / should redirect to /static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")
