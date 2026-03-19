import json
from typing import List, Optional
from openai import AzureOpenAI

from core.settings import settings
from services.ai.prompt_builder import PromptBuilder

class AIAnalysisResult:
    
    def __init__(self, raw_response: dict, segment_number: int):
        self.raw_response = raw_response
        self.segment_number = segment_number
        self.user_match = raw_response.get("user_match", {})
        self.technical_quality = raw_response.get("technical_quality", {})

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
        frames_base64: List[str],
        description: Optional[str],
        hashtags: Optional[List[str]],
        music: Optional[str],
        user_state_json: str
    ) -> AIAnalysisResult:
        
        prompt = PromptBuilder.build_prompt(
            user_state_json=user_state_json,
            segment_number=segment_number,
            description=description,
            hashtags=hashtags,
            music=music
        )
        
        message_content = [{"type": "text", "text": prompt}]
        
        for frame_base64 in frames_base64:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_base64}"
                }
            })
        
        print(f"       Calling AI (model: gpt-4.1-mini, segment {segment_number}, {len(frames_base64)} frames)...")
        
        try:
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
            
            response_text = response.choices[0].message.content
            
            if not response_text:
                print(f"       AI returned empty")
                return self._get_empty_result(segment_number)
            
            clean_response = self._clean_response(response_text)
            parsed = json.loads(clean_response)
            
            print(f"       AI analysis complete")
            print(f"         USER MATCH:")
            print(f"         - Emotions: {parsed.get('user_match', {}).get('emotions', [])}")
            print(f"         - Language: {parsed.get('user_match', {}).get('language_code', 'None')}")
            print(f"         - Topic: {parsed.get('user_match', {}).get('topic', 'None')}")
            print(f"         TECHNICAL QUALITY:")
            print(f"         - Visual Dynamics: {parsed.get('technical_quality', {}).get('visual_dynamics', False)}")
            print(f"         - High Production Value: {parsed.get('technical_quality', {}).get('high_production_value', False)}")
            print(f"         - Clear Punchline: {parsed.get('technical_quality', {}).get('clear_punchline', False)}")
            print(f"         - Known Music Detected: {parsed.get('technical_quality', {}).get('known_music_detected', False)}")
            print(f"         - Retention Curve Rising: {parsed.get('technical_quality', {}).get('retention_curve_rising', False)}")
            
            return AIAnalysisResult(parsed, segment_number)
            
        except json.JSONDecodeError as e:
            print(f"        JSON parse error: {e}")
            print(f"      Decision tree will use available data only")
            return self._get_empty_result(segment_number)
        
        except Exception as e:
            print(f"        AI call failed: {type(e).__name__}: {e}")
            print(f"      Decision tree will use available data only")
            return self._get_empty_result(segment_number)
    
    def _clean_response(self, response_text: str) -> str:
        clean = response_text.strip()
        
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        
        if clean.endswith("```"):
            clean = clean[:-3]
        
        return clean.strip()
    
    def _get_empty_result(self, segment_number: int) -> AIAnalysisResult:
        return AIAnalysisResult({
            "user_match": {
                "emotions": [],
                "language_code": None,
                "topic": None
            },
            "technical_quality": {
                "visual_dynamics": False,
                "high_production_value": False,
                "clear_punchline": False,
                "known_music_detected": False,
                "retention_curve_rising": False
            }
        }, segment_number)