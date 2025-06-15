

import asyncio
import argparse
from typing import Dict, Any, List
from agents.planner import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.synthesis_agent import SynthesisAgent
from utils.config import settings

class MultiAgentOrchestrator:
    """Orchestrates the execution of multiple agents to achieve a goal."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.synthesis_agent = SynthesisAgent()
        self.iteration_count = 0
    
    async def execute(self, goal: str) -> Dict[str, Any]:
        """Execute the multi-agent system to achieve the given goal."""
        print(f"\nProcessing goal: {goal}")
        
        # Step 1: Planning
        plan_result = await self.planner.process({"goal": goal})
        print("\nPlanning phase completed")
        
        # Step 2: Execute agents in order
        agent_order = plan_result.get("agent_order", [])
        
        # CHANGED: The initial 'current_data' now directly uses the planner's output,
        # ensuring the plan is passed along correctly.
        current_data = {
            "data": plan_result.get("data", {}),
            "context": {
                "goal": goal,
            }
        }
        
        for agent_name in agent_order:
            print(f"\nExecuting {agent_name} agent...")
            agent = self._get_agent(agent_name)
            if agent:
                # The output of one agent becomes the direct input for the next.
                current_data = await agent.process(current_data)
                
                # Check if we need to iterate
                while agent.should_continue() and self.iteration_count < settings.MAX_ITERATIONS:
                    self.iteration_count += 1
                    print(f"\nIteration {self.iteration_count} for {agent_name} agent...")
                    current_data = await agent.process(current_data)
            else:
                print(f"Warning: Unknown agent {agent_name}")
        
        # Step 3: Final evaluation
        final_evaluation = await self._evaluate_final_output(current_data, goal)
        
        return {
            "final_output": current_data,
            "evaluation": final_evaluation,
            "iterations": self.iteration_count,
            "agent_order": agent_order
        }
    
    def _get_agent(self, agent_name: str):
        """Get the appropriate agent instance based on name."""
        agents = {
            "research": self.research_agent,
            "analysis": self.analysis_agent,
            "synthesis": self.synthesis_agent
        }
        return agents.get(agent_name.lower().strip()) # CHANGED: Make it case-insensitive and robust to whitespace
    
    async def _evaluate_final_output(self, final_output: Dict[str, Any], original_goal: str) -> Dict[str, Any]:
        """Evaluate the final output against the original goal."""
        # Use the planner to evaluate goal satisfaction
        satisfaction_score = await self.planner.evaluate_goal_satisfaction( # CHANGED: Made this async to match other calls
            final_output,
            original_goal
        )
        
        return {
            "goal_satisfaction": satisfaction_score,
            "iterations_required": self.iteration_count,
            "success": satisfaction_score >= settings.CONFIDENCE_THRESHOLD
        }

async def main():
    parser = argparse.ArgumentParser(description="Multi-Agent AI System")
    parser.add_argument("--goal", required=True, help="The goal to achieve")
    args = parser.parse_args()
    
    orchestrator = MultiAgentOrchestrator()
    result = await orchestrator.execute(args.goal)
    
    print("\n=== Final Results ===")
    print(f"Goal Satisfaction: {result['evaluation']['goal_satisfaction']:.2f}")
    print(f"Iterations Required: {result['iterations']}")
    print(f"Success: {result['evaluation']['success']}")
    print("\nFinal Output:")
    
    # CHANGED: More robustly parse the final output
    final_data = result.get('final_output', {}).get('data', {})
    formatted_output = final_data.get('formatted_output', {})
    if isinstance(formatted_output, dict):
        print(formatted_output.get('formatted_text', 'No formatted output available.'))
    elif isinstance(final_data, dict):
        print(final_data.get('synthesized_output', 'No final synthesis available.'))
    else:
        print(final_data)

if __name__ == "__main__":
    asyncio.run(main())