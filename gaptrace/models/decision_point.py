"""Core data models for AST analysis and coverage mapping"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class DecisionType(str, Enum):
    """Types of decision points in code"""
    IF_CONDITION = "if"
    ELSE_BRANCH = "else"
    SWITCH_CASE = "switch"
    LOOP_CONDITION = "for/while"
    FUNCTION_CALL = "call"
    NULL_CHECK = "null_check"
    ERROR_RETURN = "error_return"
    ARITHMETIC_OP = "arithmetic"
    LOGICAL_OP = "logical"
    COMPARISON = "comparison"


@dataclass
class Coverage:
    """Coverage information for a line/branch"""
    line_number: int
    execution_count: int = 0
    is_covered: bool = False
    branches_total: int = 0
    branches_covered: int = 0
    
    def coverage_percentage(self) -> float:
        """Calculate branch coverage percentage"""
        if self.branches_total == 0:
            return 100.0 if self.is_covered else 0.0
        return (self.branches_covered / self.branches_total) * 100


@dataclass
class DecisionPoint:
    """Represents a decision/branch point in code"""
    function_name: str
    decision_type: DecisionType
    line_number: int
    condition_text: str
    file_path: str
    
    # Coverage information
    coverage: Optional[Coverage] = None
    
    # Additional context
    nesting_level: int = 0
    is_critical: bool = False  # High-importance decision (null checks, error handling)
    
    def is_covered(self) -> bool:
        """Check if this decision point is covered"""
        return self.coverage is not None and self.coverage.is_covered
    
    def coverage_percent(self) -> float:
        """Get coverage percentage"""
        if self.coverage is None:
            return 0.0
        return self.coverage.coverage_percentage()
    
    def __hash__(self):
        """Make hashable for deduplication"""
        return hash((self.function_name, self.line_number, self.condition_text))
    
    def __eq__(self, other):
        """Equality for deduplication"""
        if not isinstance(other, DecisionPoint):
            return False
        return (self.function_name == other.function_name and 
                self.line_number == other.line_number and
                self.condition_text == other.condition_text)


@dataclass
class FunctionAnalysis:
    """Analysis results for a single function"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    decision_points: List[DecisionPoint] = field(default_factory=list)
    total_branches: int = 0
    covered_branches: int = 0
    
    def branch_coverage(self) -> float:
        """Calculate branch coverage percentage"""
        if self.total_branches == 0:
            return 100.0
        return (self.covered_branches / self.total_branches) * 100
    
    def uncovered_decisions(self) -> List[DecisionPoint]:
        """Get all uncovered decision points"""
        return [dp for dp in self.decision_points if not dp.is_covered()]
    
    def critical_gaps(self) -> List[DecisionPoint]:
        """Get uncovered critical decision points (null checks, error handling)"""
        return [dp for dp in self.uncovered_decisions() if dp.is_critical]


@dataclass
class ParseResult:
    """Result of parsing a C++ source file"""
    file_path: str
    functions: Dict[str, FunctionAnalysis] = field(default_factory=dict)
    total_decision_points: int = 0
    covered_decision_points: int = 0
    
    def all_decision_points(self) -> List[DecisionPoint]:
        """Get all decision points across all functions"""
        points = []
        for func in self.functions.values():
            points.extend(func.decision_points)
        return points
    
    def uncovered_decision_points(self) -> List[DecisionPoint]:
        """Get all uncovered decision points"""
        return [dp for dp in self.all_decision_points() if not dp.is_covered()]
    
    def critical_gaps(self) -> Dict[str, List[DecisionPoint]]:
        """Get critical gaps by function"""
        gaps = {}
        for func_name, func in self.functions.items():
            critical = func.critical_gaps()
            if critical:
                gaps[func_name] = critical
        return gaps
    
    def coverage_percentage(self) -> float:
        """Calculate overall coverage percentage"""
        if self.total_decision_points == 0:
            return 100.0
        return (self.covered_decision_points / self.total_decision_points) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "file": self.file_path,
            "total_decision_points": self.total_decision_points,
            "covered_decision_points": self.covered_decision_points,
            "coverage_percentage": self.coverage_percentage(),
            "functions": {
                name: {
                    "name": func.name,
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                    "total_branches": func.total_branches,
                    "covered_branches": func.covered_branches,
                    "branch_coverage": func.branch_coverage(),
                    "decision_points": [
                        {
                            "line": dp.line_number,
                            "type": dp.decision_type.value,
                            "condition": dp.condition_text,
                            "covered": dp.is_covered(),
                            "coverage_percent": dp.coverage_percent(),
                        }
                        for dp in func.decision_points
                    ]
                }
                for name, func in self.functions.items()
            }
        }
