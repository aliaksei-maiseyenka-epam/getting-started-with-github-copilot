from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_delete_participant_unregisters_student():
    activity_name = "Chess Club"
    email = "test-delete-student@mergington.edu"

    signup_resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_resp.status_code == 200

    delete_resp = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert delete_resp.status_code == 200
    assert email not in delete_resp.json()["participants"]

def test_delete_participant_rejects_missing_student():
    activity_name = "Chess Club"
    email = "missing-student@mergington.edu"

    delete_resp = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert delete_resp.status_code == 400
    assert "not signed up" in delete_resp.json()["detail"]
