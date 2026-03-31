from dataclasses import dataclass

@dataclass(frozen=True)
class EngagementResult:
    level: str
    total_engagement: int
    weighted_score: int

class EngagementAnalyzer:    
    WEIGHTS = {
        'likes': 1,
        'comments': 2,
        'reposts': 3,
        'shares': 3,
    }
    
    THRESHOLDS = {
        'viral_very_high': 100_000,
        'viral_high': 50_000,
        'popular': 10_000,
        'growing': 1_000,
    }
    
    @staticmethod
    def analyze(
        likes_count: int | None = None,
        comments_count: int | None = None,
        reposts_count: int | None = None,
        shares_count: int | None = None
    ) -> EngagementResult:
        metrics = EngagementAnalyzer._build_metrics(
            likes_count,
            comments_count,
            reposts_count,
            shares_count
        )
        
        total_engagement = sum(metrics.values())
        weighted_score = EngagementAnalyzer._calculate_weighted_score(metrics)
        level = EngagementAnalyzer._determine_engagement_level(weighted_score)
        
        return EngagementResult(
            level=level,
            total_engagement=total_engagement,
            weighted_score=weighted_score
        )
    
    @staticmethod
    def _build_metrics(
        likes_count: int | None,
        comments_count: int | None,
        reposts_count: int | None,
        shares_count: int | None
    ) -> dict[str, int]:
        return {
            'likes': likes_count or 0,
            'comments': comments_count or 0,
            'reposts': reposts_count or 0,
            'shares': shares_count or 0,
        }
    
    @staticmethod
    def _calculate_weighted_score(metrics: dict[str, int]) -> int:
        return sum(
            metrics[metric] * EngagementAnalyzer.WEIGHTS[metric]
            for metric in metrics
        )
    
    @staticmethod
    def _determine_engagement_level(weighted_score: int) -> str:
        if weighted_score > EngagementAnalyzer.THRESHOLDS['viral_very_high']:
            return "Viral (Very high engagement)"
        elif weighted_score > EngagementAnalyzer.THRESHOLDS['viral_high']:
            return "Viral (High engagement)"
        elif weighted_score > EngagementAnalyzer.THRESHOLDS['popular']:
            return "Popular (Moderate engagement)"
        elif weighted_score > EngagementAnalyzer.THRESHOLDS['growing']:
            return "Growing (Low engagement)"
        else:
            return "New (Minimal engagement)"