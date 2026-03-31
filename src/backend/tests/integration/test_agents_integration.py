import json

class TestAgentsIntegration:
    def test_get_platforms_requires_auth(self, client):
        response = client.get("/api/platforms")
        assert response.status_code == 401
    
    def test_get_platforms_success(self, authenticated_client):
        response = authenticated_client.get("/api/platforms")
        
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        assert isinstance(data["platforms"], list)
        assert len(data["platforms"]) == 3
        assert "YouTube" in data["platforms"]
        assert "TikTok" in data["platforms"]
        assert "Instagram" in data["platforms"]
    
    def test_get_predictor_versions_success(self, authenticated_client):
        response = authenticated_client.get("/api/predictor-versions")
        
        assert response.status_code == 200
        data = response.json()
        assert "versions" in data
        assert isinstance(data["versions"], list)
        assert "v1" in data["versions"]
        assert "v2" in data["versions"]
    
    def test_create_agent_success(self, authenticated_client, valid_user_profile):
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "test_agent_001",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_agent_001"
        assert data["platform"] == "YouTube"
        assert data["predictor_version"] == "v1"
        assert data["state"] == "offline"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_agent_invalid_platform(self, authenticated_client, valid_user_profile):
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "test_agent",
                "platform": "Facebook",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "UNSUPPORTED_PLATFORM"
    
    def test_create_agent_invalid_predictor_version(self, authenticated_client, valid_user_profile):
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "test_agent",
                "platform": "YouTube",
                "predictor_version": "v999",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "predictor" in data["error"].lower() or "version" in data["error"].lower()
    
    def test_create_agent_name_too_long(self, authenticated_client, valid_user_profile):
        long_name = "a" * 256
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": long_name,
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "too long" in data["error"].lower()
        assert "255" in data["error"]
    
    def test_create_agent_missing_required_field(self, authenticated_client, valid_user_profile):
        response = authenticated_client.post(
            "/api/agents",
            json={
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        assert response.status_code == 400
    
    def test_create_agent_invalid_json_profile(self, authenticated_client):
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "test_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": "not valid json"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "json" in data["error"].lower()
    
    def test_create_agent_missing_user_profile_field(self, authenticated_client):
        invalid_profile = {
            "user_profile": {
                "user_email": "test@example.com"
            }
        }
        
        response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "test_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(invalid_profile)
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "missing required field" in data["error"].lower()
    
    def test_list_agents_empty(self, authenticated_client):
        response = authenticated_client.get("/api/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)
        assert data["total"] == 0
    
    def test_list_agents_with_data(self, authenticated_client, valid_user_profile):
        authenticated_client.post(
            "/api/agents",
            json={
                "name": "agent1",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        authenticated_client.post(
            "/api/agents",
            json={
                "name": "agent2",
                "platform": "TikTok",
                "predictor_version": "v2",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        response = authenticated_client.get("/api/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["agents"]) == 2
    
    def test_list_agents_filter_by_state(self, authenticated_client, valid_user_profile):
        authenticated_client.post(
            "/api/agents",
            json={
                "name": "offline_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        response = authenticated_client.get("/api/agents?state=offline")
        
        assert response.status_code == 200
        data = response.json()
        assert all(agent["state"] == "offline" for agent in data["agents"])
    
    def test_get_agent_by_id(self, authenticated_client, valid_user_profile):
        create_response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "get_test_agent",
                "platform": "Instagram",
                "predictor_version": "v2",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        agent_id = create_response.json()["id"]
        
        response = authenticated_client.get(f"/api/agents/{agent_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == "get_test_agent"
        assert data["platform"] == "Instagram"
    
    def test_get_nonexistent_agent(self, authenticated_client):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.get(f"/api/agents/{fake_uuid}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "AGENT_NOT_FOUND"
    
    def test_update_agent_name(self, authenticated_client, valid_user_profile):
        create_response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "original_name",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        agent_id = create_response.json()["id"]
        
        response = authenticated_client.put(
            f"/api/agents/{agent_id}",
            json={"name": "updated_name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated_name"
        assert data["platform"] == "YouTube"
    
    def test_update_agent_platform(self, authenticated_client, valid_user_profile):
        create_response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "test_agent",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        agent_id = create_response.json()["id"]
        
        response = authenticated_client.put(
            f"/api/agents/{agent_id}",
            json={"platform": "TikTok"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "TikTok"
    
    def test_delete_agent_success(self, authenticated_client, valid_user_profile):
        create_response = authenticated_client.post(
            "/api/agents",
            json={
                "name": "to_delete",
                "platform": "YouTube",
                "predictor_version": "v1",
                "state_file_data": json.dumps(valid_user_profile)
            }
        )
        
        agent_id = create_response.json()["id"]
        
        response = authenticated_client.delete(f"/api/agents/{agent_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()
        
        get_response = authenticated_client.get(f"/api/agents/{agent_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_agent(self, authenticated_client):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.delete(f"/api/agents/{fake_uuid}")
        
        assert response.status_code == 404