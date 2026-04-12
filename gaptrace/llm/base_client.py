"""Abstract base class for LLM clients"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """Abstract LLM client interface"""
    
    @abstractmethod
    def describe_gap(
        self,
        function_name: str,
        decision_type: str,
        line_number: int,
        source_code: Optional[str] = None
    ) -> str:
        """Generate a description of a missing test scenario
        
        Args:
            function_name: Name of the function
            decision_type: Type of decision (if, switch, loop, etc.)
            line_number: Line number of the decision
            source_code: Optional context from source code
            
        Returns:
            Human-readable description of the missing scenario
        """
        pass
    
    def batch_describe_gaps(self, gaps: list) -> dict:
        """Describe multiple gaps (default: process one by one)
        
        Args:
            gaps: List of gap dictionaries
            
        Returns:
            Dictionary mapping gap line numbers to descriptions
        """
        results = {}
        for gap in gaps:
            desc = self.describe_gap(
                gap.get("function_name"),
                gap.get("decision_type"),
                gap.get("line_number"),
                gap.get("source_code")
            )
            results[gap.get("line_number")] = desc
        return results
