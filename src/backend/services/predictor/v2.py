import os
import time
import json
import sys
import warnings
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['FFREPORT'] = 'level=quiet'
os.environ['AV_LOG_FORCE_NOCOLOR'] = '1'

from domain.video import VideoSource, VideoPlatform
from domain.action import PredictedActionType, PredictedAction
from services.predictor.base import BasePredictor
from services.video_processor.video_processor import VideoProcessor
from services.predictor.initial_analysis import InitialAnalyzer
from services.predictor.segment_analyzer import SegmentAnalyzer
from services.decision_tree.decision_engine import DecisionEngine, DecisionContext
from services.video_log_service import VideoLogService
from schemas.predict import VideoMetadata

class PredictorV2(BasePredictor):
    
    NO_SEGMENT_PLATFORMS = {VideoPlatform.TIKTOK}
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.initial_analyzer = InitialAnalyzer()
        self.segment_analyzer = SegmentAnalyzer()
    
    async def predict_with_context(
        self,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        user_state_json: str,
        check_video_existence: bool = True,
        db: Optional[AsyncSession] = None,
        session_id: Optional[UUID] = None,
        agent_id: Optional[UUID] = None,
    ) -> List[str]:
        
        print(f"\n{'='*80}")
        print(f" PREDICTOR V2 - Starting Analysis")
        print(f"{'='*80}")
        
        overall_start = time.time()

        user_state = json.loads(user_state_json)
        user_triggers = user_state.get('user_profile', {}).get('retention_triggers', {})
        
        initial_analysis = await self.initial_analyzer.analyze(
            video_metadata=video_metadata,
            user_state_json=user_state_json,
            verbose=True
        )
        
        if video_metadata.video_time_duration is None:
            print(f"\n  No duration - metadata-only decision\n")
            
            context = DecisionContext(
                segment_number=1,
                total_segments=1,
                video_duration=0,
                current_video_time=0,
                initial_analysis=initial_analysis,
                segment_analysis=None,
                previous_actions=[],
                description=video_metadata.description,
                hashtags=video_metadata.hashtags,
                user_state=user_triggers
            )
            
            actions = DecisionEngine.decide(context)
            final_actions = DecisionEngine.convert_actions_to_response(actions)
            
            if db and session_id and agent_id:
                await self._log_video(
                    db, session_id, agent_id, video_source, video_metadata,
                    final_actions, user_state_json, []
                )
            
            return final_actions
        
        duration = video_metadata.video_time_duration
        
        if duration < 6 or duration > 180:
            print(f"\n  Duration {duration}s out of range - SKIP\n")
            
            final_actions = ["skip"]
            
            if db and session_id and agent_id:
                await self._log_video(
                    db, session_id, agent_id, video_source, video_metadata,
                    final_actions, user_state_json, []
                )
            
            return final_actions
        
        print(f" Video Duration: {duration}s")
        
        processing_result = self.video_processor.prepare_video_processing(
            video_source=video_source,
            duration=duration,
            video_author=video_metadata.video_author
        )
        
        if processing_result.skipped:
            final_actions = ["skip"]
            
            if db and session_id and agent_id:
                await self._log_video(
                    db, session_id, agent_id, video_source, video_metadata,
                    final_actions, user_state_json, []
                )
            
            return final_actions
        
        print(f" Analyzing {len(processing_result.segments)} segments\n")
        
        all_actions = []
        segment_times = []
        segment_analyses = []
        
        for idx, (start, end) in enumerate(processing_result.segments, 1):
            print(f"{'-'*80}")
            print(f" Segment {idx}/{len(processing_result.segments)} ({start:.1f}s - {end:.1f}s)")
            print(f"{'-'*80}\n")
            
            segment_start = time.time()
            
            video_file, _ = self.video_processor.download_segment(
                url=processing_result.url,
                start_time=start,
                end_time=end,
                segment_number=idx,
                total_segments=len(processing_result.segments),
                download_full=processing_result.download_full
            )
            
            try:
                segment_analysis = await self.segment_analyzer.analyze(
                    video_file=video_file,
                    segment_number=idx,
                    start_time=start,
                    end_time=end,
                    duration=duration,
                    description=video_metadata.description,
                    hashtags=video_metadata.hashtags,
                    user_state_json=user_state_json
                )
                segment_analyses.append(segment_analysis)
            except Exception as e:
                print(f"        Analysis failed: {e}")
                segment_analysis = None
            
            self._cleanup_file(video_file)
            
            segment_elapsed = time.time() - segment_start
            segment_times.append(segment_elapsed)
            
            context = DecisionContext(
                segment_number=idx,
                total_segments=len(processing_result.segments),
                video_duration=duration,
                current_video_time=start,
                initial_analysis=initial_analysis,
                segment_analysis=segment_analysis,
                previous_actions=all_actions,
                description=video_metadata.description,
                hashtags=video_metadata.hashtags,
                user_state=user_triggers
            )
            
            actions = DecisionEngine.decide(context)
            
            print(f"\n       Decision: {[a.to_string() for a in actions]}")
            print(f"        Segment time: {segment_elapsed:.2f}s\n")
            
            all_actions.extend(actions)
            
            if any(a.action_type == PredictedActionType.SKIP for a in actions):
                print(f" SKIP detected - stopping analysis\n")
                break
        
        all_actions = self._adjust_continue_watching(all_actions, segment_times)
        
        has_skip = any(a.action_type == PredictedActionType.SKIP for a in all_actions)
        if not has_skip:
            print(f" Adding final SKIP action")
            all_actions.append(PredictedAction(PredictedActionType.SKIP))
        
        total_time = time.time() - overall_start
        
        print(f"{'='*80}")
        print(f" Complete in {total_time:.2f}s")
        
        final_actions = DecisionEngine.convert_actions_to_response(all_actions)
        
        print(f"   Final Actions: {final_actions}")
        print(f"{'='*80}\n")
        
        if db and session_id and agent_id:
            await self._log_video(
                db, session_id, agent_id, video_source, video_metadata,
                final_actions, user_state_json, segment_analyses
            )
        
        return final_actions
    
    async def _log_video(
        self,
        db: AsyncSession,
        session_id: UUID,
        agent_id: UUID,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        predicted_actions: List[str],
        user_state_json: str,
        segment_analyses: List
    ):
        try:
            await VideoLogService.log_video(
                db=db,
                session_id=session_id,
                agent_id=agent_id,
                video_source=video_source,
                video_metadata=video_metadata,
                predicted_actions=predicted_actions,
                user_state_json=user_state_json,
                segment_analyses=segment_analyses
            )
            print(f" Video logged to database")
        except Exception as e:
            print(f"  Failed to log video: {e}")
    
    def _adjust_continue_watching(
        self,
        actions: List[PredictedAction],
        segment_times: List[float]
    ) -> List[PredictedAction]:
        adjusted = []
        total_time_spent = sum(segment_times)
        
        has_skip = any(a.action_type == PredictedActionType.SKIP for a in actions)
        
        for action in actions:
            if action.action_type == PredictedActionType.CONTINUE_WATCHING and has_skip:
                if action.seconds:
                    adjusted_seconds = max(1, action.seconds - int(total_time_spent))
                    
                    if adjusted_seconds <= int(total_time_spent):
                        continue
                    
                    action.seconds = adjusted_seconds
            
            adjusted.append(action)
        
        return adjusted
    
    def _cleanup_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
    
    def predict(self, video_source: VideoSource, check_video_existence: bool = True) -> List[PredictedActionType]:
        raise NotImplementedError("V2 predictor requires async predict_with_context method")
    
    def _predict_from_data(self, data) -> List[PredictedActionType]:
        raise NotImplementedError("V2 predictor requires async predict_with_context method")