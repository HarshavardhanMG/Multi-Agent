
from typing import Dict, Any, List
from .base_agent import BaseAgent
from utils.config import settings
import google.generativeai as genai
import json # Make sure json is imported

class AnalysisAgent(BaseAgent):
    """Agent responsible for analyzing and processing data."""
    
    def __init__(self):
        super().__init__("analysis")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze the input data."""
        data = input_data.get("data", {})
        context = input_data.get("context", {})
        goal = context.get("goal", "")
        
        if not goal:
            # This is a fallback, the main error was happening below
            return self._create_error_output("No goal specified in context", context)
        
        research_summary = data.get("research_summary")
        if not research_summary:
            return self._create_error_output("No research summary provided for analysis", context)

        try:
            analysis_prompt = f"""
            Analyze the following research summary in the context of the user's goal.
            
            Goal: {goal}
            
            Research Summary:
            {research_summary}
            
            Provide a detailed analysis. Extract key insights and list actionable recommendations.
            Structure your response as a JSON object with three keys: "analysis_text", "insights", and "recommendations".
            "insights" and "recommendations" should be lists of strings.
            ONLY return the raw JSON object.
            """
            
            response = self.model.generate_content(analysis_prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            analysis_data = json.loads(json_text)

            output = {
                "data": {
                    "research_summary": research_summary,
                    "source_data": data.get("source_data", {}),
                    "analysis": analysis_data.get("analysis_text", ""),
                    "insights": analysis_data.get("insights", []),
                    "recommendations": analysis_data.get("recommendations", []),
                },
                "context": context,
                "status": "completed"
            }
            
            self.update_confidence(0.9) # CHANGED: Set a high confidence on success to prevent looping
            self.add_to_history(input_data, output)
            return output
            
        except Exception as e:
            # CHANGED: Pass the original context to the error function
            error_message = f"Error performing analysis: {str(e)}. Raw LLM response: {response.text if 'response' in locals() else 'N/A'}"
            print(error_message) # Print the detailed error for debugging
            return self._create_error_output(error_message, context)

    # CHANGED: The function now accepts and preserves the original context.
    def _create_error_output(self, error_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create an error output with appropriate structure, preserving context."""
        # On error, we set confidence low so should_continue() could be true,
        # but the orchestrator loop is the main driver. This ensures the agent state is 'failed'.
        self.update_confidence(0.1) 
        
        error_context = context.copy()
        error_context["error"] = error_message

        return {
            "data": {
                "analysis": f"Error: {error_message}",
                "insights": [],
                "recommendations": []
            },
            "context": error_context, # Return the preserved context with the error added
            "status": "error"
        }