
from typing import Dict, Any, List
from .base_agent import BaseAgent
from utils.config import settings
import google.generativeai as genai
import json

class PlannerAgent(BaseAgent):
    """Agent responsible for planning and coordinating the execution of other agents."""
    
    def __init__(self):
        super().__init__("planner")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20') # CHANGED: Using gemini-pro for better structured output
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user goal and create an execution plan."""
        if not isinstance(input_data, dict):
            return self._create_error_output("Invalid input data format")
            
        goal = input_data.get("goal", "")
        
        if not goal:
            return self._create_error_output("No goal specified")
        
        # CHANGED: Prompt is now much more specific to get structured output
        prompt = f"""
        Given the goal: "{goal}"
        
        1.  Create a step-by-step plan to achieve this goal.
        2.  Based on your plan, determine the necessary sequence of agents to execute. The available agents are [research, analysis, synthesis].
        
        Respond with a JSON object with two keys: "plan" (a string containing the detailed plan) and "agent_order" (a list of strings with the agent names in order).
        Example:
        {{
            "plan": "First, research the topic to gather data. Second, analyze the collected data for key insights. Third, synthesize the findings into a final report.",
            "agent_order": ["research", "analysis", "synthesis"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        
        # CHANGED: Robust JSON parsing
        try:
            # Clean the response to extract only the JSON part
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            plan_data = json.loads(json_text)
            plan = plan_data.get("plan", "No plan generated.")
            agent_order = plan_data.get("agent_order", ["synthesis"])
        except (json.JSONDecodeError, AttributeError):
            plan = response.text
            agent_order = self._determine_agent_order_fallback(plan)
        
        output = {
            "data": {
                "plan": plan
            },
            "context": {
                "goal": goal
            },
            "agent_order": agent_order,
            "status": "planned"
        }
        
        self.update_confidence(0.9)
        self.add_to_history(input_data, output)
        
        return output
    
    def _create_error_output(self, error_message: str) -> Dict[str, Any]:
        return {
            "data": {"plan": f"Error: {error_message}"},
            "context": {"error": error_message},
            "agent_order": [],
            "status": "error"
        }
    
    def _determine_agent_order_fallback(self, plan: str) -> List[str]:
        # NEW: A slightly more robust fallback if JSON parsing fails
        plan_lower = plan.lower()
        order = []
        if "research" in plan_lower or "gather" in plan_lower or "collect" in plan_lower:
            order.append("research")
        if "analysis" in plan_lower or "analyze" in plan_lower or "insights" in plan_lower:
            order.append("analysis")
        if "synthesis" in plan_lower or "summarize" in plan_lower or "report" in plan_lower:
            order.append("synthesis")
        
        return order if order else ["research", "analysis", "synthesis"]
    
    async def evaluate_goal_satisfaction(self, final_output: Dict[str, Any], original_goal: str) -> float:
        """Evaluate how well the final output satisfies the original goal."""
        if not isinstance(final_output, dict):
            return 0.0
            
        output_text = json.dumps(final_output.get("data", {}))
        
        # CHANGED: More specific prompt to ensure a float is returned
        prompt = f"""
        Original Goal: {original_goal}
        
        Final Output:
        {output_text}
        
        Evaluate how well the output satisfies the goal. Consider completeness, relevance, and clarity.
        Respond with a single floating-point number between 0.0 (not satisfied at all) and 1.0 (perfectly satisfied).
        ONLY return the number.
        """
        
        response = self.model.generate_content(prompt)
        try:
            satisfaction_score = float(response.text.strip())
            return min(max(satisfaction_score, 0.0), 1.0)
        except (ValueError, AttributeError):
            return 0.5