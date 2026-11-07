import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Robotics Club": {
                "description": "Build and program robots",
                "schedule": "Mondays, 3:30 PM",
                "max_participants": 3,
                "participants": ["existing@school.edu"],
            }
        },
    )
    return TestClient(app_module.app)


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_activities = app_module.activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "new@school.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    activities_response = client.get("/activities")
    assert activities_response.json()[activity_name]["participants"] == [
        "existing@school.edu",
        email,
    ]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "existing@school.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert app_module.activities[activity_name]["participants"] == [email]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@school.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "existing@school.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    activities_response = client.get("/activities")
    assert activities_response.json()[activity_name]["participants"] == []


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "missing@school.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert app_module.activities[activity_name]["participants"] == [
        "existing@school.edu"
    ]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@school.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}