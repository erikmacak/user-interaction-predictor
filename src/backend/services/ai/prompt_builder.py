import json
from dataclasses import dataclass

@dataclass(frozen=True)
class UserState:
    preferred_emotions: list[str]
    preferred_languages: list[str]
    interest_topics: list[str]
    
    @classmethod
    def from_json(cls, user_state_json: str) -> "UserState":
        try:
            state = json.loads(user_state_json)
            profile = state.get("user_profile", {})
            triggers = profile.get("retention_triggers", {})
            
            return cls(
                preferred_emotions=triggers.get("preferred_emotions", []),
                preferred_languages=triggers.get("preferred_languages", []),
                interest_topics=triggers.get("interest_topics", []),
            )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error parsing user state: {e}")
            return cls(
                preferred_emotions=[],
                preferred_languages=[],
                interest_topics=[],
            )
    
    def emotions_as_string(self) -> str:
        return ", ".join(self.preferred_emotions) if self.preferred_emotions else "Not specified"
    
    def languages_as_string(self) -> str:
        return ", ".join(self.preferred_languages) if self.preferred_languages else "Not specified"
    
    def topics_as_string(self) -> str:
        return ", ".join(self.interest_topics) if self.interest_topics else "Not specified"


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
    def build_prompt(
        user_state_json: str,
        segment_number: int,
        description: str | None,
        hashtags: list[str] | None,
        music: str | None
    ) -> str:
        user_state = UserState.from_json(user_state_json)
        
        description_str = description if description else "Not provided"
        hashtags_str = ", ".join(hashtags) if hashtags else "Not provided"
        music_str = music if music else "No music detected"
        
        return PromptBuilder.SYSTEM_PROMPT_TEMPLATE.format(
            preferred_emotions=user_state.emotions_as_string(),
            preferred_languages=user_state.languages_as_string(),
            interest_topics=user_state.topics_as_string(),
            segment_number=segment_number,
            description=description_str,
            hashtags=hashtags_str,
            music=music_str
        )