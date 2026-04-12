"""OpenAI LLM client (to be implemented)"""

from typing import Optional

from .base_client import LLMClient


class OpenAIClient(LLMClient):
    """OpenAI GPT-4o client for gap scenario descriptions
    
    To use this client:
    1. Get API key from https://platform.openai.com/api-keys
    2. Set environment variable: export OPENAI_API_KEY="sk-..."
    3. Call: analyzer = GapAnalyzer(llm_client=OpenAIClient())
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            
        Raises:
            ValueError: If API key not provided and env var not set
        """
        import os

        from openai import OpenAI as OpenAILib
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable:\n"
                "  export OPENAI_API_KEY='sk-...'\n"
                "Get your key from: https://platform.openai.com/api-keys"
            )
        
        self.client = OpenAILib(api_key=self.api_key)
    
    def describe_gap(
        self,
        function_name: str,
        decision_type: str,
        line_number: int,
        source_code: Optional[str] = None
    ) -> str:
        """Generate a description using OpenAI GPT-4o
        
        Args:
            function_name: Name of the function
            decision_type: Type of decision (if, switch, loop, etc.)
            line_number: Line number of the decision
            source_code: Optional source code context
            
        Returns:
            Description of missing test scenario from GPT-4o
            
        Raises:
            Exception: If API call fails
        """
        source_context = f"Source Code Context:\n{source_code}" if source_code else ""
        
        prompt = f"""You are a software testing expert. A code analysis tool found an uncovered code path.

Function: {function_name}()
Decision Type: {decision_type}
Line Number: {line_number}
{source_context}

Generate a concise description (1-2 sentences) of what test scenario is missing. Focus on what input/condition should be tested, and why it matters."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}") from e
