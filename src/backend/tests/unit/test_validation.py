import json

class TestUserProfileValidation:
    def test_missing_email_field(self):
        from domain.user_profile_schema import UserProfileSchema
        
        invalid_profile = json.dumps({
            "user_profile": {
                "gender": "male",
                "country_code": "us",
                "date_of_birth": "15.03.1998",
                "favorite_authors": [],
                "retention_triggers": {
                    "preferred_emotions": ["curiosity"],
                    "preferred_languages": ["en"],
                    "interest_topics": ["tech"]
                }
            }
        })
        
        is_valid, error_message = UserProfileSchema.validate(invalid_profile)
        
        assert not is_valid
        assert "user_email" in error_message.lower()
    
    def test_missing_gender_field(self):
        from domain.user_profile_schema import UserProfileSchema
        
        invalid_profile = json.dumps({
            "user_profile": {
                "user_email": "test@example.com",
                "country_code": "us",
                "date_of_birth": "15.03.1998",
                "favorite_authors": [],
                "retention_triggers": {
                    "preferred_emotions": ["curiosity"],
                    "preferred_languages": ["en"],
                    "interest_topics": ["tech"]
                }
            }
        })
        
        is_valid, error_message = UserProfileSchema.validate(invalid_profile)
        
        assert not is_valid
        assert "gender" in error_message.lower()
    
    def test_missing_retention_triggers(self):
        from domain.user_profile_schema import UserProfileSchema
        
        invalid_profile = json.dumps({
            "user_profile": {
                "user_email": "test@example.com",
                "gender": "male",
                "country_code": "us",
                "date_of_birth": "15.03.1998",
                "favorite_authors": []
            }
        })
        
        is_valid, error_message = UserProfileSchema.validate(invalid_profile)
        
        assert not is_valid
        assert "retention_triggers" in error_message.lower()
    
    def test_valid_profile(self):
        from domain.user_profile_schema import UserProfileSchema
        
        valid_profile = json.dumps({
            "user_profile": {
                "user_email": "test@example.com",
                "gender": "male",
                "country_code": "us",
                "date_of_birth": "15.03.1998",
                "favorite_authors": ["author1"],
                "retention_triggers": {
                    "preferred_emotions": ["curiosity", "amusement"],
                    "preferred_languages": ["en"],
                    "interest_topics": ["tech", "coding"]
                }
            }
        })
        
        is_valid, error_message = UserProfileSchema.validate(valid_profile)
        
        assert is_valid
        assert error_message is None or error_message == ""
    
    def test_invalid_json_format(self):
        from domain.user_profile_schema import UserProfileSchema
        
        invalid_json = "not a valid json"
        
        is_valid, error_message = UserProfileSchema.validate(invalid_json)
        
        assert not is_valid