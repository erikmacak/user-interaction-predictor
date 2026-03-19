from typing import List, Dict, Any
import json

class UserProfileSchema:
    
    REQUIRED_STRUCTURE = {
        "user_profile": {
            "user_email": str,
            "gender": str,
            "country_code": str,
            "date_of_birth": str,
            "favorite_authors": list,
            "retention_triggers": {
                "preferred_emotions": list,
                "preferred_languages": list,
                "interest_topics": list,
            }
        }
    }
    
    @classmethod
    def validate(cls, json_str: str) -> tuple[bool, str | None]:

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        
        if "user_profile" not in data:
            return False, "Missing required field: 'user_profile'"
        
        profile = data["user_profile"]
        
        required_fields = ["user_email", "gender", "country_code", "date_of_birth", "favorite_authors", "retention_triggers"]
        for field in required_fields:
            if field not in profile:
                return False, f"Missing required field: 'user_profile.{field}'"

        if not isinstance(profile.get("user_email"), str):
            return False, "Field 'user_profile.user_email' must be a string"
        
        if not isinstance(profile.get("gender"), str):
            return False, "Field 'user_profile.gender' must be a string"
        
        if not isinstance(profile.get("country_code"), str):
            return False, "Field 'user_profile.country_code' must be a string"
        
        if not isinstance(profile.get("date_of_birth"), str):
            return False, "Field 'user_profile.date_of_birth' must be a string"
        
        if not isinstance(profile.get("favorite_authors"), list):
            return False, "Field 'user_profile.favorite_authors' must be an array"
        
        if not isinstance(profile.get("retention_triggers"), dict):
            return False, "Field 'user_profile.retention_triggers' must be an object"
        
        triggers = profile["retention_triggers"]
        required_trigger_fields = ["preferred_emotions", "preferred_languages", "interest_topics"]
        
        for field in required_trigger_fields:
            if field not in triggers:
                return False, f"Missing required field: 'user_profile.retention_triggers.{field}'"
            
            if not isinstance(triggers[field], list):
                return False, f"Field 'user_profile.retention_triggers.{field}' must be an array"
        
        return True, None
    
    @classmethod
    def get_example_schema(cls) -> Dict[str, Any]:
        return {
            "user_profile": {
                "user_email": "john.techie@gmail.com",
                "gender": "male",
                "country_code": "us",
                "date_of_birth": "15.03.1998",
                "favorite_authors": ["mkbhd", "unboxtherapy", "mrwhosetheboss"],
                "retention_triggers": {
                    "preferred_emotions": [
                        "curiosity",
                        "amusement",
                        "surprise"
                    ],
                    "preferred_languages": ["en"],
                    "interest_topics": [
                        "artificial_intelligence",
                        "consumer_electronics"
                    ]
                }
            }
        }