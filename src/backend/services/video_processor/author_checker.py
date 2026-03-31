import json

class AuthorChecker:    
    @staticmethod
    def is_favorite_author(
        video_author: str | None,
        user_state_json: str
    ) -> bool:
        if not video_author:
            return False
        
        try:
            user_state = json.loads(user_state_json)
            favorite_authors = AuthorChecker._extract_favorite_authors(user_state)
            
            if favorite_authors is None:
                return False
            
            return AuthorChecker._is_author_in_favorites(video_author, favorite_authors)
            
        except (json.JSONDecodeError, KeyError):
            return False
    
    @staticmethod
    def _extract_favorite_authors(user_state: dict) -> list[str] | None:
        favorite_authors = user_state.get("user_profile", {}).get("favorite_authors")
        
        if favorite_authors is None:
            return None
        
        if isinstance(favorite_authors, str):
            return [favorite_authors]
        
        if not isinstance(favorite_authors, list):
            return None
        
        return favorite_authors
    
    @staticmethod
    def _is_author_in_favorites(video_author: str, favorite_authors: list) -> bool:
        video_author_lower = video_author.lower().strip()
        favorites_lower = [str(author).lower().strip() for author in favorite_authors]
        
        return video_author_lower in favorites_lower