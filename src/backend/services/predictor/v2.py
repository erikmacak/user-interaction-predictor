import os
import time
import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.platform import VideoPlatform
from domain.video import VideoSource
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
    
    MIN_DURATION = 6
    MAX_DURATION = 180
    
    SEPARATOR = "=" * 80
    SUBSEPARATOR = "-" * 80
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.initial_analyzer = InitialAnalyzer()
        self.segment_analyzer = SegmentAnalyzer()
    
    async def predict_with_context(
        self,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        user_state_json: str,
        db: AsyncSession | None = None,
        session_id: UUID | None = None,
        agent_id: UUID | None = None,
    ) -> list[str]:
        self._print_header()
        
        overall_start = time.time()
        
        user_triggers = self._parse_user_triggers(user_state_json)
        
        initial_analysis = await self.initial_analyzer.analyze(
            video_metadata=video_metadata,
            user_state_json=user_state_json,
            verbose=True
        )
        
        if not self._has_valid_duration(video_metadata):
            return await self._handle_no_duration(
                video_metadata, initial_analysis, user_triggers,
                db, session_id, agent_id, video_source, user_state_json
            )
        
        duration = video_metadata.video_time_duration
        
        if not self._is_duration_in_range(duration):
            return await self._handle_out_of_range_duration(
                duration, db, session_id, agent_id,
                video_source, video_metadata, user_state_json
            )
        
        print(f" Video Duration: {duration}s")
        
        processing_result = self.video_processor.prepare_video_processing(
            video_source=video_source,
            duration=duration,
            video_author=video_metadata.video_author
        )
        
        if processing_result.skipped:
            return await self._handle_skipped_video(
                db, session_id, agent_id,
                video_source, video_metadata, user_state_json
            )
        
        use_full_video_strategy = self._should_use_full_video_strategy(
            video_source.platform,
            processing_result.download_full
        )
        
        if use_full_video_strategy:
            final_actions = await self._analyze_full_video(
                processing_result=processing_result,
                video_source=video_source,
                video_metadata=video_metadata,
                user_state_json=user_state_json,
                initial_analysis=initial_analysis,
                user_triggers=user_triggers,
                duration=duration
            )
        else:
            final_actions = await self._analyze_segments(
                processing_result=processing_result,
                video_metadata=video_metadata,
                user_state_json=user_state_json,
                initial_analysis=initial_analysis,
                user_triggers=user_triggers,
                duration=duration
            )
        
        total_time = time.time() - overall_start
        
        self._print_footer(total_time, final_actions)
        
        if self._should_log_video(db, session_id, agent_id):
            segment_analyses = getattr(self, '_current_segment_analyses', [])
            await self._log_video(
                db, session_id, agent_id, video_source,
                video_metadata, final_actions, user_state_json, segment_analyses
            )
        
        return final_actions
    
    def _should_use_full_video_strategy(
        self,
        platform: VideoPlatform,
        download_full: bool
    ) -> bool:
        return platform in self.NO_SEGMENT_PLATFORMS or download_full
    
    async def _analyze_full_video(
        self,
        processing_result,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        user_state_json: str,
        initial_analysis,
        user_triggers: dict,
        duration: int
    ) -> list[str]:
        print(f"\n{self.SEPARATOR}")
        print(f" Platform {video_source.platform.value} - Full video analysis")
        print(f" Downloading complete video with enhanced frame extraction")
        print(f"{self.SEPARATOR}\n")
        
        video_file = self._download_segment_file(
            processing_result, 0, duration, 1, 1
        )
        
        segment_analysis = await self._analyze_single_segment(
            video_file=video_file,
            segment_number=1,
            start_time=0,
            end_time=duration,
            duration=duration,
            video_metadata=video_metadata,
            user_state_json=user_state_json,
            is_full_video=True
        )
        
        self._cleanup_file(video_file)
        
        if not segment_analysis:
            return ["skip"]
        
        self._current_segment_analyses = [segment_analysis]
        
        actions = self._make_decision(
            segment_number=1,
            total_segments=1,
            video_duration=duration,
            current_time=0,
            initial_analysis=initial_analysis,
            segment_analysis=segment_analysis,
            previous_actions=[],
            video_metadata=video_metadata,
            user_triggers=user_triggers
        )
        
        final_actions = self._finalize_actions(actions, [0])
        
        return DecisionEngine.convert_actions_to_response(final_actions)
    
    async def _analyze_segments(
        self,
        processing_result,
        video_metadata: VideoMetadata,
        user_state_json: str,
        initial_analysis,
        user_triggers: dict,
        duration: int
    ) -> list[str]:
        print(f" Analyzing {len(processing_result.segments)} segments\n")
        
        all_actions = []
        segment_times = []
        segment_analyses = []
        
        for idx, (start, end) in enumerate(processing_result.segments, 1):
            self._print_segment_header(idx, len(processing_result.segments), start, end)
            
            segment_start = time.time()
            
            video_file = self._download_segment_file(
                processing_result, start, end, idx, len(processing_result.segments)
            )
            
            segment_analysis = await self._analyze_single_segment(
                video_file=video_file,
                segment_number=idx,
                start_time=start,
                end_time=end,
                duration=duration,
                video_metadata=video_metadata,
                user_state_json=user_state_json,
                is_full_video=False
            )
            
            if segment_analysis:
                segment_analyses.append(segment_analysis)
            
            self._cleanup_file(video_file)
            
            segment_elapsed = time.time() - segment_start
            segment_times.append(segment_elapsed)
            
            actions = self._make_decision(
                segment_number=idx,
                total_segments=len(processing_result.segments),
                video_duration=duration,
                current_time=start,
                initial_analysis=initial_analysis,
                segment_analysis=segment_analysis,
                previous_actions=all_actions,
                video_metadata=video_metadata,
                user_triggers=user_triggers
            )
            
            self._print_segment_result(actions, segment_elapsed)
            
            all_actions.extend(actions)
            
            if self._should_stop_analysis(actions):
                print(f" SKIP detected - stopping analysis\n")
                break
        
        self._current_segment_analyses = segment_analyses
        
        all_actions = self._finalize_actions(all_actions, segment_times)
        
        return DecisionEngine.convert_actions_to_response(all_actions)
    
    def _download_segment_file(
        self,
        processing_result,
        start: float,
        end: float,
        idx: int,
        total_segments: int
    ) -> str:
        video_file, _ = self.video_processor.download_segment(
            url=processing_result.url,
            start_time=start,
            end_time=end,
            segment_number=idx,
            total_segments=total_segments,
            download_full=processing_result.download_full
        )
        return video_file
    
    async def _analyze_single_segment(
        self,
        video_file: str,
        segment_number: int,
        start_time: float,
        end_time: float,
        duration: int,
        video_metadata: VideoMetadata,
        user_state_json: str,
        is_full_video: bool = False
    ):
        try:
            return await self.segment_analyzer.analyze(
                video_file=video_file,
                segment_number=segment_number,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                description=video_metadata.description,
                hashtags=video_metadata.hashtags,
                user_state_json=user_state_json,
                is_full_video=is_full_video
            )
        except Exception as e:
            print(f"        Analysis failed: {e}")
            return None
    
    def _make_decision(
        self,
        segment_number: int,
        total_segments: int,
        video_duration: int,
        current_time: float,
        initial_analysis,
        segment_analysis,
        previous_actions: list[PredictedAction],
        video_metadata: VideoMetadata,
        user_triggers: dict
    ) -> list[PredictedAction]:
        context = DecisionContext(
            segment_number=segment_number,
            total_segments=total_segments,
            video_duration=video_duration,
            current_video_time=current_time,
            initial_analysis=initial_analysis,
            segment_analysis=segment_analysis,
            previous_actions=previous_actions,
            description=video_metadata.description,
            hashtags=video_metadata.hashtags,
            user_state=user_triggers
        )
        
        return DecisionEngine.decide(context)
    
    def _finalize_actions(
        self,
        all_actions: list[PredictedAction],
        segment_times: list[float]
    ) -> list[PredictedAction]:
        all_actions = self._adjust_continue_watching(all_actions, segment_times)
        
        has_skip = any(a.action_type == PredictedActionType.SKIP for a in all_actions)
        if not has_skip:
            print(f"\n ! Adding final SKIP action !")
            all_actions.append(PredictedAction(PredictedActionType.SKIP))
        
        return all_actions
    
    async def _handle_no_duration(
        self,
        video_metadata: VideoMetadata,
        initial_analysis,
        user_triggers: dict,
        db: AsyncSession | None,
        session_id: UUID | None,
        agent_id: UUID | None,
        video_source: VideoSource,
        user_state_json: str
    ) -> list[str]:
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
        
        if self._should_log_video(db, session_id, agent_id):
            await self._log_video(
                db, session_id, agent_id, video_source,
                video_metadata, final_actions, user_state_json, []
            )
        
        return final_actions
    
    async def _handle_out_of_range_duration(
        self,
        duration: int,
        db: AsyncSession | None,
        session_id: UUID | None,
        agent_id: UUID | None,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        user_state_json: str
    ) -> list[str]:
        print(f"\n  Duration {duration}s out of range - SKIP\n")
        
        final_actions = ["skip"]
        
        if self._should_log_video(db, session_id, agent_id):
            await self._log_video(
                db, session_id, agent_id, video_source,
                video_metadata, final_actions, user_state_json, []
            )
        
        return final_actions
    
    async def _handle_skipped_video(
        self,
        db: AsyncSession | None,
        session_id: UUID | None,
        agent_id: UUID | None,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        user_state_json: str
    ) -> list[str]:
        final_actions = ["skip"]
        
        if self._should_log_video(db, session_id, agent_id):
            await self._log_video(
                db, session_id, agent_id, video_source,
                video_metadata, final_actions, user_state_json, []
            )
        
        return final_actions
    
    async def _log_video(
        self,
        db: AsyncSession,
        session_id: UUID,
        agent_id: UUID,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        predicted_actions: list[str],
        user_state_json: str,
        segment_analyses: list
    ) -> None:
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
            print(f" Video logged to database\n")
        except Exception as e:
            print(f"  Failed to log video: {e}")
    
    def _adjust_continue_watching(
        self,
        actions: list[PredictedAction],
        segment_times: list[float]
    ) -> list[PredictedAction]:
        adjusted = []
        total_time_spent = sum(segment_times)
        
        has_skip = any(a.action_type == PredictedActionType.SKIP for a in actions)
        
        for action in actions:
            if self._should_adjust_watching_time(action, has_skip, total_time_spent):
                adjusted_seconds = max(1, action.seconds - int(total_time_spent))
                
                if adjusted_seconds <= int(total_time_spent):
                    continue
                
                action = action.with_seconds(adjusted_seconds)
            
            adjusted.append(action)
        
        return adjusted
    
    @staticmethod
    def _should_adjust_watching_time(
        action: PredictedAction,
        has_skip: bool,
        total_time_spent: float
    ) -> bool:
        return (
            action.action_type == PredictedActionType.CONTINUE_WATCHING
            and has_skip
            and action.seconds is not None
        )
    
    @staticmethod
    def _cleanup_file(file_path: str) -> None:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
    
    @staticmethod
    def _parse_user_triggers(user_state_json: str) -> dict:
        user_state = json.loads(user_state_json)
        return user_state.get('user_profile', {}).get('retention_triggers', {})
    
    @staticmethod
    def _has_valid_duration(video_metadata: VideoMetadata) -> bool:
        return video_metadata.video_time_duration is not None
    
    @staticmethod
    def _is_duration_in_range(duration: int) -> bool:
        return PredictorV2.MIN_DURATION <= duration <= PredictorV2.MAX_DURATION
    
    @staticmethod
    def _should_log_video(
        db: AsyncSession | None,
        session_id: UUID | None,
        agent_id: UUID | None
    ) -> bool:
        return db is not None and session_id is not None and agent_id is not None
    
    @staticmethod
    def _should_stop_analysis(actions: list[PredictedAction]) -> bool:
        return any(a.action_type == PredictedActionType.SKIP for a in actions)
    
    @staticmethod
    def _print_header() -> None:
        print(f"\n{PredictorV2.SEPARATOR}")
        print(f" PREDICTOR V2 - Starting Analysis")
        print(f"{PredictorV2.SEPARATOR}")
    
    @staticmethod
    def _print_segment_header(idx: int, total: int, start: float, end: float) -> None:
        print(f"{PredictorV2.SUBSEPARATOR}")
        print(f" Segment {idx}/{total} ({start:.1f}s - {end:.1f}s)")
        print(f"{PredictorV2.SUBSEPARATOR}\n")
    
    @staticmethod
    def _print_segment_result(actions: list[PredictedAction], elapsed: float) -> None:
        print(f"\n       Decision: {[a.to_string() for a in actions]}")
        print(f"\n       Segment time: {elapsed:.2f}s\n")
    
    @staticmethod
    def _print_footer(total_time: float, final_actions: list[str]) -> None:
        print(f"{PredictorV2.SEPARATOR}")
        print(f" Complete in {total_time:.2f}s")
        print(f"   Final Actions: {final_actions}")
        print(f"{PredictorV2.SEPARATOR}\n")
    
    def predict(
        self,
        video_source: VideoSource,
        check_video_existence: bool = True
    ) -> list[PredictedActionType]:
        raise NotImplementedError("V2 predictor requires async predict_with_context method")
    
    def _predict_from_data(self, data: dict) -> list[PredictedActionType]:
        raise NotImplementedError("V2 predictor requires async predict_with_context method")