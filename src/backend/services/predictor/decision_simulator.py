import random
from enum import Enum

class SimulatedDecision(Enum):
    CONTINUE = "continue"
    SKIP = "skip"

class DecisionSimulator:
    
    def __init__(self, skip_probability: float = 0.25):
        self.skip_probability = skip_probability
    
    def should_skip(self, segment_number: int) -> bool:
        return random.random() < self.skip_probability
    
    def get_decision(self, segment_number: int) -> SimulatedDecision:
        return SimulatedDecision.SKIP if self.should_skip(segment_number) else SimulatedDecision.CONTINUE