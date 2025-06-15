

from typing import Dict, Any, List
from .base_agent import BaseAgent
from utils.config import settings
import google.generativeai as genai
import json

class SynthesisAgent(BaseAgent):
    """Agent responsible for synthesizing information into a final output."""
    
    def __init__(self):
        super().__init__("synthesis")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and synthesize the input data into a final output."""
        data_to_synthesize = input_data.get("data", {})
        context = input_data.get("context", {})
        goal = context.get("goal", "")
        
        if not goal:
            # CHANGED: Pass context to the error function
            return self._create_error_output("No goal specified in context", context)
        
        # If the previous step had an error, just format that error for the user.
        if "error" in context:
            error_message = context["error"]
            return self._create_error_output(f"Could not complete request due to a previous error: {error_message}", context)

        synthesis_prompt = f"""
        Your task is to create a final, comprehensive report based on the provided data and analysis to meet the user's goal.

        User Goal: {goal}

        Available Data & Analysis:
        {json.dumps(data_to_synthesize, indent=2)}

        Synthesize all this information into a coherent, well-structured report. The report should include:
        1.  An Executive Summary.
        2.  Key Findings (based on insights).
        3.  A Detailed Analysis section.
        4.  Actionable Recommendations.

        Present this as a single, formatted text output.
        """
        
        response = self.model.generate_content(synthesis_prompt)
        synthesized_text = response.text
        
        output = {
            "data": {
                # Pass through previous data
                **data_to_synthesize,
                # Add new synthesis data
                "synthesized_output": synthesized_text,
                "formatted_output": {
                    "formatted_text": synthesized_text
                }
            },
            "context": context,
            "status": "completed"
        }
        
        self.update_confidence(0.95)
        self.add_to_history(input_data, output)
        
        return output
    
    # CHANGED: The function now accepts and preserves the original context.
    def _create_error_output(self, error_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create an error output with appropriate structure, preserving context."""
        self.update_confidence(0.1)

        error_context = context.copy()
        error_context["error"] = error_message

        return {
            "data": {
                "synthesized_output": f"Error: {error_message}",
                "formatted_output": {"formatted_text": f"Error: {error_message}"}
            },
            "context": error_context,
            "status": "error"
        }