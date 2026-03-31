import asyncio
from dataclasses import dataclass

from schemas.predict import VideoMetadata
from services.video_processor.engagement_analyzer import EngagementAnalyzer, EngagementResult
from services.video_processor.author_checker import AuthorChecker

@dataclass(frozen=True)
class InitialAnalysisResult:
    engagement: EngagementResult
    is_favorite_author: bool
    video_author: str | None

class InitialAnalyzer:
    SEPARATOR = "-" * 80
    
    @staticmethod
    async def analyze(
        video_metadata: VideoMetadata,
        user_state_json: str,
        verbose: bool = False
    ) -> InitialAnalysisResult:
        if verbose:
            InitialAnalyzer._print_header()
        
        engagement_result, is_favorite = await InitialAnalyzer._run_parallel_analysis(
            video_metadata,
            user_state_json,
            verbose
        )
        
        if verbose:
            InitialAnalyzer._print_footer()
        
        return InitialAnalysisResult(
            engagement=engagement_result,
            is_favorite_author=is_favorite,
            video_author=video_metadata.video_author
        )
    
    @staticmethod
    async def _run_parallel_analysis(
        video_metadata: VideoMetadata,
        user_state_json: str,
        verbose: bool
    ) -> tuple[EngagementResult, bool]:
        engagement_task = asyncio.create_task(
            InitialAnalyzer._analyze_engagement(video_metadata, verbose)
        )
        author_task = asyncio.create_task(
            InitialAnalyzer._check_favorite_author(
                video_metadata.video_author,
                user_state_json,
                verbose
            )
        )
        
        return await asyncio.gather(engagement_task, author_task)
    
    @staticmethod
    async def _analyze_engagement(
        video_metadata: VideoMetadata,
        verbose: bool
    ) -> EngagementResult:
        result = EngagementAnalyzer.analyze(
            likes_count=video_metadata.likes_count,
            comments_count=video_metadata.comments_count,
            reposts_count=video_metadata.reposts_count,
            shares_count=video_metadata.shares_count
        )
        
        if verbose:
            InitialAnalyzer._print_engagement_results(video_metadata, result)
        
        return result
    
    @staticmethod
    async def _check_favorite_author(
        video_author: str | None,
        user_state_json: str,
        verbose: bool
    ) -> bool:
        is_favorite = AuthorChecker.is_favorite_author(video_author, user_state_json)
        
        if verbose:
            InitialAnalyzer._print_author_check(video_author, is_favorite)
        
        return is_favorite
    
    @staticmethod
    def _print_header() -> None:
        print(f" Initial Analysis (First Segment Only)")
        print(InitialAnalyzer.SEPARATOR)
    
    @staticmethod
    def _print_footer() -> None:
        print(f"{InitialAnalyzer.SEPARATOR}\n")
    
    @staticmethod
    def _print_engagement_results(
        video_metadata: VideoMetadata,
        result: EngagementResult
    ) -> None:
        print(f" Engagement Analysis:")
        print(f"    Likes: {video_metadata.likes_count or 0:,}")
        print(f"    Comments: {video_metadata.comments_count or 0:,}")
        print(f"    Reposts: {video_metadata.reposts_count or 0:,}")
        print(f"    Shares: {video_metadata.shares_count or 0:,}")
        print(f"    Total: {result.total_engagement:,}")
        print(f"    Weighted Score: {result.weighted_score:,}")
        print(f"    Level: {result.level}")
    
    @staticmethod
    def _print_author_check(video_author: str | None, is_favorite: bool) -> None:
        print(f"\n Author Check:")
        print(f"    Author: {video_author or 'Unknown'}")
        print(f"    Is Favorite: {' Yes' if is_favorite else ' No'}")