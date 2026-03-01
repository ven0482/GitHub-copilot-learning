import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture that runs around each test to restore the inin-memory
    `activities` dictionary to its original state.
    """
    original = copy.deepcopy(activities)
    yield
    # teardown: clear and restore
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange
    # (fixture has already reset state)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_new_student():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    assert email in activities[activity]["participants"]


def test_signup_duplicate_failure():
    # Arrange
    activity = "Programming Class"
    email = "emma@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    detail = response.json().get("detail", "").lower()
    assert "already signed up" in detail or "already registered" in detail


def test_unregister_student():
    # Arrange
    activity = "Gym Class"
    email = "john@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert f"Unregistered {email}" in response.json()["message"]
    assert email not in activities[activity]["participants"]
