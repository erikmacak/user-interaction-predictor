from typing import Optional
from dataclasses import dataclass

@dataclass
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
        likes_count: Optional[int] = None,
        comments_count: Optional[int] = None,
        reposts_count: Optional[int] = None,
        shares_count: Optional[int] = None
    ) -> EngagementResult:
        metrics = {
            'likes': likes_count or 0,
            'comments': comments_count or 0,
            'reposts': reposts_count or 0,
            'shares': shares_count or 0,
        }
        
        total_engagement = sum(metrics.values())
        
        weighted_score = sum(
            metrics[metric] * EngagementAnalyzer.WEIGHTS[metric]
            for metric in metrics
        )
        
        if weighted_score > EngagementAnalyzer.THRESHOLDS['viral_very_high']:
            level = "Viral (Very high engagement)"
        elif weighted_score > EngagementAnalyzer.THRESHOLDS['viral_high']:
            level = "Viral (High engagement)"
        elif weighted_score > EngagementAnalyzer.THRESHOLDS['popular']:
            level = "Popular (Moderate engagement)"
        elif weighted_score > EngagementAnalyzer.THRESHOLDS['growing']:
            level = "Growing (Low engagement)"
        else:
            level = "New (Minimal engagement)"
        
        return EngagementResult(
            level=level,
            total_engagement=total_engagement,
            weighted_score=weighted_score
        )