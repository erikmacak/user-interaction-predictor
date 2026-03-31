import json
from typing import Any

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
    
    _PROFILE_FIELDS = {
        "user_email": str,
        "gender": str,
        "country_code": str,
        "date_of_birth": str,
        "favorite_authors": list,
        "retention_triggers": dict,
    }
    
    _TRIGGER_FIELDS = {
        "preferred_emotions": list,
        "preferred_languages": list,
        "interest_topics": list,
    }
    
    @classmethod
    def validate(cls, json_str: str) -> tuple[bool, str | None]:
        data = cls._parse_json(json_str)
        if isinstance(data, str):
            return False, data
        
        profile = cls._validate_root_structure(data)
        if isinstance(profile, str):
            return False, profile
        
        error = cls._validate_profile_fields(profile)
        if error:
            return False, error
        
        error = cls._validate_retention_triggers(profile["retention_triggers"])
        if error:
            return False, error
        
        return True, None
    
    @classmethod
    def _parse_json(cls, json_str: str) -> dict[str, Any] | str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return f"Invalid JSON format: {str(e)}"
    
    @classmethod
    def _validate_root_structure(cls, data: dict[str, Any]) -> dict[str, Any] | str:
        if "user_profile" not in data:
            return "Missing required field: 'user_profile'"
        return data["user_profile"]
    
    @classmethod
    def _validate_profile_fields(cls, profile: dict[str, Any]) -> str | None:
        for field_name, field_type in cls._PROFILE_FIELDS.items():
            if field_name not in profile:
                return f"Missing required field: 'user_profile.{field_name}'"
            
            if not isinstance(profile[field_name], field_type):
                type_name = cls._get_type_name(field_type)
                return f"Field 'user_profile.{field_name}' must be {type_name}"
        
        return None
    
    @classmethod
    def _validate_retention_triggers(cls, triggers: dict[str, Any]) -> str | None:
        for field_name, field_type in cls._TRIGGER_FIELDS.items():
            if field_name not in triggers:
                return f"Missing required field: 'user_profile.retention_triggers.{field_name}'"
            
            if not isinstance(triggers[field_name], field_type):
                type_name = cls._get_type_name(field_type)
                return f"Field 'user_profile.retention_triggers.{field_name}' must be {type_name}"
        
        return None
    
    @classmethod
    def _get_type_name(cls, field_type: type) -> str:
        type_names = {
            str: "a string",
            list: "an array",
            dict: "an object",
        }
        return type_names.get(field_type, str(field_type))