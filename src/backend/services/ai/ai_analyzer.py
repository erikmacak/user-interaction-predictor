import json
from dataclasses import dataclass

from openai import AzureOpenAI

from core.settings import settings
from services.ai.prompt_builder import PromptBuilder

@dataclass(frozen=True)
class AIAnalysisResult:
    user_match: dict
    technical_quality: dict
    segment_number: int
    
    @classmethod
    def from_response(cls, raw_response: dict, segment_number: int) -> "AIAnalysisResult":
        return cls(
            user_match=raw_response.get("user_match", {}),
            technical_quality=raw_response.get("technical_quality", {}),
            segment_number=segment_number
        )
    
    @classmethod
    def empty(cls, segment_number: int) -> "AIAnalysisResult":
        return cls(
            user_match={
                "emotions": [],
                "language_code": None,
                "topic": None
            },
            technical_quality={
                "visual_dynamics": False,
                "high_production_value": False,
                "clear_punchline": False,
                "known_music_detected": False,
                "retention_curve_rising": False
            },
            segment_number=segment_number
        )

class AIAnalyzer:    
    def __init__(self):
        self.client = AzureOpenAI(
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
        )
    
    async def analyze_segment(
        self,
        segment_number: int,
        frames_base64: list[str],
        description: str | None,
        hashtags: list[str] | None,
        music: str | None,
        user_state_json: str
    ) -> AIAnalysisResult:
        prompt = PromptBuilder.build_prompt(
            user_state_json=user_state_json,
            segment_number=segment_number,
            description=description,
            hashtags=hashtags,
            music=music
        )
        
        message_content = self._build_message_content(prompt, frames_base64)
        
        print(f"       Calling AI (model: gpt-4.1-mini, segment {segment_number}, {len(frames_base64)} frames)...")
        
        try:
            response_text = await self._call_ai(message_content)
            
            if not response_text:
                print(f"       AI returned empty")
                return AIAnalysisResult.empty(segment_number)
            
            parsed = self._parse_response(response_text)
            self._log_analysis_result(parsed)
            
            return AIAnalysisResult.from_response(parsed, segment_number)
            
        except json.JSONDecodeError as e:
            print(f"        JSON parse error: {e}")
            print(f"      Decision tree will use available data only")
            return AIAnalysisResult.empty(segment_number)
        
        except Exception as e:
            print(f"        AI call failed: {type(e).__name__}: {e}")
            print(f"      Decision tree will use available data only")
            return AIAnalysisResult.empty(segment_number)
    
    def _build_message_content(self, prompt: str, frames_base64: list[str]) -> list[dict]:
        message_content = [{"type": "text", "text": prompt}]
        
        for frame_base64 in frames_base64:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_base64}"
                }
            })
        
        return message_content
    
    async def _call_ai(self, message_content: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            max_completion_tokens=1000,
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        
        return response.choices[0].message.content or ""
    
    def _parse_response(self, response_text: str) -> dict:
        clean_response = self._clean_response(response_text)
        return json.loads(clean_response)
    
    def _clean_response(self, response_text: str) -> str:
        clean = response_text.strip()
        
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        
        if clean.endswith("```"):
            clean = clean[:-3]
        
        return clean.strip()
    
    def _log_analysis_result(self, parsed: dict) -> None:
        user_match = parsed.get('user_match', {})
        tech_quality = parsed.get('technical_quality', {})
        
        print(f"       AI analysis complete")
        print(f"         USER MATCH:")
        print(f"         - Emotions: {user_match.get('emotions', [])}")
        print(f"         - Language: {user_match.get('language_code', 'None')}")
        print(f"         - Topic: {user_match.get('topic', 'None')}")
        print(f"         TECHNICAL QUALITY:")
        print(f"         - Visual Dynamics: {tech_quality.get('visual_dynamics', False)}")
        print(f"         - High Production Value: {tech_quality.get('high_production_value', False)}")
        print(f"         - Clear Punchline: {tech_quality.get('clear_punchline', False)}")
        print(f"         - Known Music Detected: {tech_quality.get('known_music_detected', False)}")
        print(f"         - Retention Curve Rising: {tech_quality.get('retention_curve_rising', False)}")