"""Mock LLM client for testing without API key"""

from typing import Optional

from .base_client import LLMClient


class MockLLMClient(LLMClient):
    """Mock LLM client for development/testing"""
    
    def __init__(self):
        """Initialize mock client"""
        self.call_count = 0
    
    def describe_gap(
        self,
        function_name: str,
        decision_type: str,
        line_number: int,
        source_code: Optional[str] = None
    ) -> str:
        """Generate a mock description
        
        Returns a template description without calling any API.
        Perfect for testing the Phase 2 flow without needing OpenAI key.
        """
        self.call_count += 1
        
        # Template descriptions based on decision type
        templates = {
            "if": f"Missing scenario: Untested {decision_type} condition in {function_name}(). "
                  f"Add a test case that triggers the False branch on line {line_number}.",
            
            "switch": f"Missing scenario: Untested case in {function_name}() switch statement. "
                     f"Add a test with an input that matches one of the unexecuted cases on line {line_number}.",
            
            "loop": f"Missing scenario: Untested loop behavior in {function_name}(). "
                   f"Add a test that exercises the loop edge case (empty, single, or maximum iterations) on line {line_number}.",
            
            "function_call": f"Missing scenario: Function {function_name}() calls another function "
                            f"on line {line_number} but no test verifies the behavior when it fails/returns error.",
            
            "default": f"Missing test scenario: Uncovered {decision_type} in {function_name}() at line {line_number}. "
                      f"Add test case for this logical path.",
        }
        
        template = templates.get(decision_type.lower(), templates["default"])
        return template
