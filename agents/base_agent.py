from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from utils.config import settings

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
        self.confidence = 0.0
        self.history: list[Dict[str, Any]] = []
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return enriched results."""
        pass
    
    def update_confidence(self, new_confidence: float) -> None:
        """Update the agent's confidence in its output."""
        self.confidence = new_confidence
    
    def add_to_history(self, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> None:
        """Add a processing step to the agent's history."""
        self.history.append({
            "input": input_data,
            "output": output_data,
            "confidence": self.confidence
        })
    
    def get_history(self) -> list[Dict[str, Any]]:
        """Get the agent's processing history."""
        return self.history
    
    def should_continue(self) -> bool:
        """Determine if the agent should continue processing based on confidence."""
        return self.confidence < settings.CONFIDENCE_THRESHOLD 