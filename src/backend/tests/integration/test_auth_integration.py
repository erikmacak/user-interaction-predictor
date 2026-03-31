class TestAuthIntegration:
    def test_login_with_valid_credentials(self, client, admin_user):
        response = client.post(
            "/api/auth/login",
            json={"password": "TestPassword123!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert isinstance(data["must_change_password"], bool)
        assert "access_token" in response.cookies
    
    def test_login_with_invalid_credentials(self, client, admin_user):
        response = client.post(
            "/api/auth/login",
            json={"password": "WrongPassword123!"}
        )
        
        assert response.status_code == 401
        data = response.json()

        assert "detail" in data or "error_code" in data
        assert "error" in data or "detail" in data
    
    def test_login_without_password(self, client, admin_user):
        response = client.post(
            "/api/auth/login",
            json={}
        )
        
        assert response.status_code == 400
    
    def test_verify_without_authentication(self, client):
        response = client.get("/api/auth/verify")
        
        assert response.status_code == 401
        data = response.json()
        assert data["error_code"] == "NOT_AUTHENTICATED"
    
    def test_verify_with_valid_authentication(self, authenticated_client):
        response = authenticated_client.get("/api/auth/verify")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["must_change_password"] is False
    
    def test_change_password_success(self, authenticated_client):
        response = authenticated_client.post(
            "/api/auth/change-password",
            json={
                "new_password": "NewSecurePass123!@",
                "confirm_password": "NewSecurePass123!@"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Password changed successfully" in data["message"]
    
    def test_change_password_mismatch(self, authenticated_client):
        response = authenticated_client.post(
            "/api/auth/change-password",
            json={
                "new_password": "NewSecurePass123!@",
                "confirm_password": "DifferentPass123!@"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "error" in data
    
    def test_change_password_too_short(self, authenticated_client):
        response = authenticated_client.post(
            "/api/auth/change-password",
            json={
                "new_password": "Short1!",
                "confirm_password": "Short1!"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_change_password_missing_uppercase(self, authenticated_client):
        response = authenticated_client.post(
            "/api/auth/change-password",
            json={
                "new_password": "nouppercase123!",
                "confirm_password": "nouppercase123!"
            }
        )
        
        assert response.status_code == 400
    
    def test_change_password_missing_special_char(self, authenticated_client):
        response = authenticated_client.post(
            "/api/auth/change-password",
            json={
                "new_password": "NoSpecialChar123",
                "confirm_password": "NoSpecialChar123"
            }
        )
        
        assert response.status_code == 400
    
    def test_logout_success(self, authenticated_client):
        response = authenticated_client.post("/api/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert "Logged out successfully" in data["message"]
        
        verify_response = authenticated_client.get("/api/auth/verify")
        assert verify_response.status_code == 401
    
    def test_logout_without_authentication(self, client):
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 200