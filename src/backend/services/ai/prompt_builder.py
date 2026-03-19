import json
from typing import List, Optional

class PromptBuilder:
    
    SYSTEM_PROMPT_TEMPLATE = """You are an expert social media analyst simulating a specific user's behavior. Your task is to analyze video metadata, visual keyframes, and music information to determine if the content matches the user's profile.

### USER STATE REPRESENTATION (The Profile you are simulating):
- Preferred Emotions: {preferred_emotions}
- Preferred Languages: {preferred_languages}
- Interest Topics: {interest_topics}

### CURRENT VIDEO DATA TO ANALYZE:
- Segment Number: {segment_number}
- Description: {description}
- Hashtags: {hashtags}
- Identified Music (Shazam): {music}
- Visual Keyframes: See attached images below

### EVALUATION RULES:
1. Identify the two most prominent emotions. If they match the "Preferred Emotions" list, return their names; otherwise, return null.
2. Determine the language code. If it matches the "Preferred Languages" list, return the code; otherwise, return null.
3. Identify the main topic. If it matches the "Interest Topics" list, return the topic name; otherwise, return null.

Additionally, provide boolean values (true/false) for:
- visual_dynamics: Does the video contain high visual movement or frequent cuts?
- high_production_value: Is the editing, lighting, and overall quality professional?
- clear_punchline: Does the video have a clear point, joke, or conclusion?
- known_music_detected: Is the background music a recognizable song or trending audio?
- retention_curve_rising: Does the video structure suggest a high probability of continued watching?

CRITICAL: Respond with ONLY a valid JSON object, nothing else. No explanations, no markdown, just JSON.

Expected JSON format:
{{
  "user_match": {{
    "emotions": ["emotion1", "emotion2"],
    "language_code": "en",
    "topic": "topic_name"
  }},
  "technical_quality": {{
    "visual_dynamics": true,
    "high_production_value": true,
    "clear_punchline": true,
    "known_music_detected": false,
    "retention_curve_rising": true
  }}
}}"""
    
    @staticmethod
    def parse_user_state(user_state_json: str) -> dict:
        try:
            state = json.loads(user_state_json)
            profile = state.get("user_profile", {})
            triggers = profile.get("retention_triggers", {})
            
            return {
                "preferred_emotions": triggers.get("preferred_emotions", []),
                "preferred_languages": triggers.get("preferred_languages", []),
                "interest_topics": triggers.get("interest_topics", []),
            }
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error parsing user state: {e}")
            return {
                "preferred_emotions": [],
                "preferred_languages": [],
                "interest_topics": [],
            }
    
    @staticmethod
    def build_prompt(
        user_state_json: str,
        segment_number: int,
        description: Optional[str],
        hashtags: Optional[List[str]],
        music: Optional[str]
    ) -> str:
        user_state = PromptBuilder.parse_user_state(user_state_json)
        
        emotions_str = ", ".join(user_state["preferred_emotions"]) if user_state["preferred_emotions"] else "Not specified"
        languages_str = ", ".join(user_state["preferred_languages"]) if user_state["preferred_languages"] else "Not specified"
        topics_str = ", ".join(user_state["interest_topics"]) if user_state["interest_topics"] else "Not specified"
        
        description_str = description if description else "Not provided"
        hashtags_str = ", ".join(hashtags) if hashtags else "Not provided"
        music_str = music if music else "No music detected"
        
        return PromptBuilder.SYSTEM_PROMPT_TEMPLATE.format(
            preferred_emotions=emotions_str,
            preferred_languages=languages_str,
            interest_topics=topics_str,
            segment_number=segment_number,
            description=description_str,
            hashtags=hashtags_str,
            music=music_str
        )