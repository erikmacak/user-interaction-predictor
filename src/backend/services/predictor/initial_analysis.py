import asyncio
from dataclasses import dataclass
from typing import Optional

from schemas.predict import VideoMetadata
from services.video_processor.engagement_analyzer import EngagementAnalyzer, EngagementResult
from services.video_processor.author_checker import AuthorChecker

@dataclass
class InitialAnalysisResult:
    engagement: EngagementResult
    is_favorite_author: bool
    video_author: Optional[str]

class InitialAnalyzer:
    
    @staticmethod
    async def analyze(
        video_metadata: VideoMetadata,
        user_state_json: str,
        verbose: bool = False
    ) -> InitialAnalysisResult:

        if verbose:
            print(f" Initial Analysis (First Segment Only)")
            print(f"{'-'*80}")
        
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
        
        engagement_result, is_favorite = await asyncio.gather(
            engagement_task,
            author_task
        )
        
        if verbose:
            print(f"{'-'*80}\n")
        
        return InitialAnalysisResult(
            engagement=engagement_result,
            is_favorite_author=is_favorite,
            video_author=video_metadata.video_author
        )
    
    @staticmethod
    async def _analyze_engagement(video_metadata: VideoMetadata, verbose: bool) -> EngagementResult:
        result = EngagementAnalyzer.analyze(
            likes_count=video_metadata.likes_count,
            comments_count=video_metadata.comments_count,
            reposts_count=video_metadata.reposts_count,
            shares_count=video_metadata.shares_count
        )
        
        if verbose:
            print(f" Engagement Analysis:")
            print(f"    Likes: {video_metadata.likes_count or 0:,}")
            print(f"    Comments: {video_metadata.comments_count or 0:,}")
            print(f"    Reposts: {video_metadata.reposts_count or 0:,}")
            print(f"    Shares: {video_metadata.shares_count or 0:,}")
            print(f"    Total: {result.total_engagement:,}")
            print(f"    Weighted Score: {result.weighted_score:,}")
            print(f"    Level: {result.level}")
        
        return result
    
    @staticmethod
    async def _check_favorite_author(
        video_author: Optional[str],
        user_state_json: str,
        verbose: bool
    ) -> bool:
        is_favorite = AuthorChecker.is_favorite_author(video_author, user_state_json)
        
        if verbose:
            print(f"\n Author Check:")
            print(f"    Author: {video_author or 'Unknown'}")
            print(f"    Is Favorite: {' Yes' if is_favorite else ' No'}")
        
        return is_favorite