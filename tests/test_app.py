from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_adds_student_to_activity():
    activity_name = "Basketball Team"
    email = "signup-student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_student():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_requires_email():
    response = client.post("/activities/Chess Club/signup")

    assert response.status_code == 422


def test_delete_participant_unregisters_student():
    activity_name = "Chess Club"
    email = "test-delete-student@mergington.edu"

    signup_resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_resp.status_code == 200

    delete_resp = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert delete_resp.status_code == 200
    assert email not in delete_resp.json()["participants"]


def test_delete_participant_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_rejects_missing_student():
    activity_name = "Chess Club"
    email = "missing-student@mergington.edu"

    delete_resp = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert delete_resp.status_code == 400
    assert "not signed up" in delete_resp.json()["detail"]


def test_delete_participant_requires_email():
    response = client.delete("/activities/Chess Club/participants")

    assert response.status_code == 422
