import pytest
import json

class TestSessionsIntegration:
    @pytest.fixture
    def test_agent(self, authenticated_client, valid_user_profile):
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "session_test_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        return response.json()
    
    def test_start_session_success(self, authenticated_client, test_agent):
        response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["agent_id"] == test_agent["id"]
        assert data["state"] == "running"
        assert data["agent_name"] == "session_test_agent"
        assert data["agent_platform"] == "YouTube"
        assert "id" in data
        assert "started_at" in data
        assert data["ended_at"] is None
    
    def test_start_session_requires_auth(self, client, test_agent):
        response = client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        assert response.status_code == 201
    
    def test_start_session_nonexistent_agent(self, authenticated_client):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": fake_uuid}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "AGENT_NOT_FOUND"
    
    def test_start_session_already_auditing(self, authenticated_client, test_agent):
        authenticated_client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "AGENT_ALREADY_AUDITING"
    
    def test_start_session_invalid_agent_id_format(self, authenticated_client):
        response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": "not-a-valid-uuid"}
        )
        
        assert response.status_code == 400
    
    def test_list_running_sessions_empty(self, authenticated_client):
        response = authenticated_client.get("/api/sessions/running")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["sessions"]) == 0
    
    def test_list_running_sessions_with_data(self, authenticated_client, test_agent):
        authenticated_client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        response = authenticated_client.get("/api/sessions/running")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["agent_name"] == "session_test_agent"
    
    def test_stop_session_success(self, authenticated_client, test_agent):
        start_response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        session_id = start_response.json()["id"]
        
        response = authenticated_client.post(f"/api/sessions/{session_id}/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert "stopped successfully" in data["message"].lower()
        
        list_response = authenticated_client.get("/api/sessions/running")
        assert list_response.json()["total"] == 0
    
    def test_stop_nonexistent_session(self, authenticated_client):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.post(f"/api/sessions/{fake_uuid}/stop")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "SESSION_NOT_FOUND"
    
    def test_stop_session_twice(self, authenticated_client, test_agent):
        start_response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": test_agent["id"]}
        )
        
        session_id = start_response.json()["id"]
        
        authenticated_client.post(f"/api/sessions/{session_id}/stop")
        
        response = authenticated_client.post(f"/api/sessions/{session_id}/stop")
        
        assert response.status_code == 409