from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_predict_endpoint_happy_path():
    response = client.post(
        "/api/predict_actions",
        json={
            "platform": "YouTube",
            "video_id": "sTh2x0yaRyU"
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert "predicted_actions" in payload
    assert isinstance(payload["predicted_actions"], list)
    assert len(payload["predicted_actions"]) > 0

def test_invalid_platform():
    response = client.post(
        "/api/predict_actions",
        json={"platform": "Facebook", "video_id": "123"},
    )
    assert response.status_code == 400

def test_nonexistent_video():
    response = client.post(
        "/api/predict_actions",
        json={"platform": "YouTube", "video_id": "this_does_not_exist"},
    )
    assert response.status_code == 404