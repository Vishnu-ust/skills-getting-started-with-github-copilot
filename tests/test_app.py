"""
Pytest tests for the Mergington High School backend.

These tests use Arrange-Act-Assert style and reset the in-memory
activities database between tests.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before and after each test."""
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9


class TestSignupForActivity:
    def test_signup_for_activity_adds_a_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 200
        assert new_email in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"

    def test_signup_for_activity_returns_404_for_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = activities[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


class TestDeleteParticipant:
    def test_delete_participant_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = activities[activity_name]["participants"][0]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
        assert email_to_remove not in activities[activity_name]["participants"]

    def test_delete_nonexistent_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        absent_email = "absent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": absent_email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up"

    def test_delete_participant_unknown_activity_returns_404(self, client):
        # Arrange
        activity_name = "Unknown Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
