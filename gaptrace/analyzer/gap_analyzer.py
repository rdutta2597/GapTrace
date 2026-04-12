"""Core gap analysis logic - finds uncovered logical paths in code"""

from dataclasses import dataclass
from typing import Dict, List

from gaptrace.models.decision_point import DecisionPoint, FunctionAnalysis, ParseResult


@dataclass
class Gap:
    """Represents a missing test scenario"""
    function_name: str
    line_number: int
    decision_type: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    

class GapAnalyzer:
    """Analyzes code to find gaps in test coverage"""
    
    def __init__(self):
        """Initialize gap analyzer"""
        self.gaps: List[Gap] = []
    
    def analyze(self, parse_result: ParseResult) -> List[Gap]:
        """Analyze parse result to find test gaps
        
        Args:
            parse_result: ParseResult from AST parser
            
        Returns:
            List of Gap objects representing missing test scenarios
        """
        self.gaps = []
        
        for func in parse_result.functions.values():
            uncovered_decisions = self._find_uncovered_decisions(func)
            for decision in uncovered_decisions:
                gap = Gap(
                    function_name=func.name,
                    line_number=decision.line_number,
                    decision_type=decision.decision_type.value,
                    description=f"Uncovered {decision.decision_type.value} at line {decision.line_number}",
                    severity=self._calculate_severity(decision, func)
                )
                self.gaps.append(gap)
        
        return self.gaps
    
    def _find_uncovered_decisions(self, func: FunctionAnalysis) -> List[DecisionPoint]:
        """Find all uncovered decision points in a function
        
        Args:
            func: FunctionAnalysis object
            
        Returns:
            List of uncovered DecisionPoint objects
        """
        uncovered = []
        for decision in func.decision_points:
            if decision.coverage and not decision.coverage.is_covered:
                uncovered.append(decision)
        return uncovered
    
    def _calculate_severity(self, decision: DecisionPoint, func: FunctionAnalysis) -> str:
        """Calculate severity of a gap
        
        Args:
            decision: The uncovered decision point
            func: The function containing it
            
        Returns:
            Severity level: "critical", "high", "medium", or "low"
        """
        # Critical: error handling, null checks, bounds checks
        if decision.is_critical:
            return "critical"
        
        # High: conditional branches with multiple outcomes
        if decision.decision_type.value in ["if", "switch"]:
            return "high"
        
        # Medium: loops
        if "loop" in decision.decision_type.value.lower():
            return "medium"
        
        # Low: function calls
        return "low"
    
    def get_critical_gaps(self) -> List[Gap]:
        """Get only critical gaps
        
        Returns:
            List of critical Gap objects
        """
        return [gap for gap in self.gaps if gap.severity == "critical"]
    
    def get_high_gaps(self) -> List[Gap]:
        """Get high severity gaps
        
        Returns:
            List of high severity Gap objects
        """
        return [gap for gap in self.gaps if gap.severity == "high"]
    
    def gap_summary(self) -> Dict:
        """Get summary of all gaps
        
        Returns:
            Dictionary with gap counts by severity
        """
        return {
            "total": len(self.gaps),
            "critical": len(self.get_critical_gaps()),
            "high": len(self.get_high_gaps()),
            "medium": len([g for g in self.gaps if g.severity == "medium"]),
            "low": len([g for g in self.gaps if g.severity == "low"]),
        }
