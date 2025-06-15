from typing import Dict, Any
from .base_agent import BaseAgent
from utils.config import settings
from utils.api_helpers import (
    get_spacex_launch,
    get_weather,
    extract_launch_location,
    analyze_weather_impact
)
import google.generativeai as genai

class ResearchAgent(BaseAgent):
    """Agent responsible for gathering relevant information."""
    
    def __init__(self):
        super().__init__("research")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input and gather relevant information."""
        context = input_data.get("context", {})
        goal = context.get("goal", "")
        plan = input_data.get("data", {}).get("plan", "")

        if not goal:
            return self._create_error_output("No goal specified in context")

        is_spacex_query = "spacex" in goal.lower() and "launch" in goal.lower()
        
        research_summary = ""
        source_data = {}

        try:
            if is_spacex_query:
                print("Conducting targeted launch research via RocketLaunch.Live...")
                launch_data = await get_spacex_launch()
                location = await extract_launch_location(launch_data)
                
                if location:
                    weather_data = await get_weather(location["lat"], location["lon"])
                    weather_analysis = analyze_weather_impact(weather_data, launch_data)
                    
                    # CHANGED: Update this section to use the new field names from RocketLaunch.Live
                    mission_name = launch_data.get('name', 'N/A')
                    launch_time = launch_data.get('t0') or launch_data.get('win_open') or 'N/A'
                    
                    # Correctly access the nested pad and location names.
                    pad_object = launch_data.get("pad", {})
                    location_object = pad_object.get("location", {})
                    launch_site_name = location_object.get("name", "Unknown Site")
                    pad_name = pad_object.get("name", "Unknown Pad")

                    research_summary = (
                        f"Research on the next SpaceX launch for goal: '{goal}'.\n"
                        f"Mission: {mission_name}\n"
                        f"Scheduled Time (UTC): {launch_time}\n"
                        f"Launch Site: {launch_site_name} - {pad_name}\n"
                        f"Weather at site: {weather_analysis['conditions']['description']}.\n"
                        f"Potential weather impacts: {', '.join(weather_analysis['potential_impacts'])}"
                    )
                    source_data = {
                        "launch_data_provider": "RocketLaunch.Live",
                        "launch_info": launch_data,
                        "weather": weather_data,
                        "weather_analysis": weather_analysis
                    }
                else:
                    research_summary = "Found a SpaceX launch but could not extract its location for weather analysis."
                    source_data = {"launch_data_provider": "RocketLaunch.Live", "launch_info": launch_data}
            else:
                print("Conducting general research...")
                research_summary = await self._general_research(goal, plan)
                source_data = {"source": "Gemini LLM"}

            # CHANGED: Unified output structure
            output = {
                "data": {
                    "research_summary": research_summary,
                    "source_data": source_data,
                },
                "context": input_data.get("context", {}), # Pass context through
                "status": "completed"
            }
            self.update_confidence(0.9) if research_summary else self.update_confidence(0.4)
            self.add_to_history(input_data, output)
            return output

        except Exception as e:
            print(f"Research agent error: {str(e)}")
            return self._create_error_output(f"An exception occurred: {e}")

    def _create_error_output(self, error_message: str) -> Dict[str, Any]:
        return {
            "data": {
                "research_summary": f"Error: {error_message}",
                "source_data": {}
            },
            "context": {"error": error_message},
            "status": "error"
        }

    async def _general_research(self, goal: str, plan: str) -> str:
        """Perform general research using Gemini."""
        prompt = f"""
        Based on the following goal and plan, conduct thorough research and provide a detailed summary.
        
        Goal: {goal}
        Execution Plan: {plan}
        
        Provide a comprehensive summary of your findings.
        """
        response = self.model.generate_content(prompt)
        return response.text