import pytest
import json

class TestVideoLogsIntegration:
    @pytest.fixture
    def test_agent_with_session(self, authenticated_client, valid_user_profile):
        agent_response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "video_log_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        agent = agent_response.json()
        
        session_response = authenticated_client.post(
            "/api/sessions",
            json={"agent_id": agent["id"]}
        )
        
        session = session_response.json()
        
        return {"agent": agent, "session": session}
    
    def test_get_agent_sessions_empty(self, authenticated_client, valid_user_profile):
        agent_response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "empty_sessions_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        agent_id = agent_response.json()["id"]
        
        response = authenticated_client.get(f"/api/agents/{agent_id}/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_export_session_requires_auth(self, client, test_agent_with_session):
        agent_id = test_agent_with_session["agent"]["id"]
        session_id = test_agent_with_session["session"]["id"]
        
        response = client.get(
            f"/api/agents/{agent_id}/sessions/{session_id}/export"
        )
        
        assert response.status_code == 404
    
    def test_export_all_agent_data_requires_auth(self, client, test_agent_with_session):
        agent_id = test_agent_with_session["agent"]["id"]
        
        response = client.get(f"/api/agents/{agent_id}/export")
        
        assert response.status_code == 404