import json
from typing import Optional

class AuthorChecker:
    
    @staticmethod
    def is_favorite_author(
        video_author: Optional[str],
        user_state_json: str
    ) -> bool:
        
        if not video_author:
            return False
        
        try:
            user_state = json.loads(user_state_json)
            favorite_authors = user_state.get("user_profile", {}).get("favorite_authors")
            
            if favorite_authors is None:
                return False

            if isinstance(favorite_authors, str):
                favorite_authors = [favorite_authors]
            
            if not isinstance(favorite_authors, list):
                return False
            
            video_author_lower = video_author.lower().strip()
            favorites_lower = [str(author).lower().strip() for author in favorite_authors]
            
            return video_author_lower in favorites_lower
            
        except (json.JSONDecodeError, KeyError):
            return False