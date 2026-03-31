import random
from enum import Enum

class SimulatedDecision(str, Enum):
    CONTINUE = "continue"
    SKIP = "skip"

class DecisionSimulator:
    DEFAULT_SKIP_PROBABILITY = 0.25
    
    def __init__(self, skip_probability: float = DEFAULT_SKIP_PROBABILITY):
        self._validate_probability(skip_probability)
        self.skip_probability = skip_probability
    
    def should_skip(self) -> bool:
        return random.random() < self.skip_probability
    
    def get_decision(self) -> SimulatedDecision:
        if self.should_skip():
            return SimulatedDecision.SKIP
        return SimulatedDecision.CONTINUE
    
    @staticmethod
    def _validate_probability(probability: float) -> None:
        if not 0.0 <= probability <= 1.0:
            raise ValueError(f"Probability must be between 0 and 1, got {probability}")