

import pytest
import asyncio
from agents.planner import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.synthesis_agent import SynthesisAgent
from main import MultiAgentOrchestrator

# A realistic goal for testing
TEST_GOAL = "Analyze the potential impact of AI on healthcare in the next decade"

@pytest.mark.asyncio
async def test_planner_agent():
    """Test the planner agent's ability to create a valid plan and agent order."""
    planner = PlannerAgent()
    input_data = {"goal": TEST_GOAL}
    
    result = await planner.process(input_data)
    
    assert "data" in result
    assert "plan" in result["data"]
    assert "agent_order" in result
    assert isinstance(result["agent_order"], list)
    assert len(result["agent_order"]) > 0
    assert result["status"] == "planned"
    assert all(isinstance(agent, str) for agent in result["agent_order"])

@pytest.mark.asyncio
async def test_research_agent():
    """Test the research agent's ability to produce a unified output structure."""
    research = ResearchAgent()
    # Input mimics what the planner would provide
    input_data = {
        "data": {"plan": "Research the topic and gather information."},
        "context": {"goal": TEST_GOAL}
    }
    
    result = await research.process(input_data)
    
    assert "data" in result
    assert "research_summary" in result["data"]
    assert "source_data" in result["data"]
    assert len(result["data"]["research_summary"]) > 0
    assert result["status"] == "completed"

@pytest.mark.asyncio
async def test_analysis_agent():
    """Test the analysis agent's ability to process the research agent's output."""
    analysis = AnalysisAgent()
    # Input mimics what the research agent would provide
    input_data = {
        "data": {
            "research_summary": "AI in healthcare shows promise in diagnostics, drug discovery, and personalized treatment. Key areas are radiology and pathology. Challenges include data privacy and regulation.",
            "source_data": {"source": "test"}
        },
        "context": {"goal": TEST_GOAL}
    }
    
    result = await analysis.process(input_data)
    
    assert "data" in result
    assert "analysis" in result["data"]
    assert "insights" in result["data"]
    assert "recommendations" in result["data"]
    assert isinstance(result["data"]["insights"], list)
    assert len(result["data"]["analysis"]) > 0
    assert result["status"] == "completed"

@pytest.mark.asyncio
async def test_synthesis_agent():
    """Test the synthesis agent's ability to create a final report."""
    synthesis = SynthesisAgent()
    # Input mimics what the analysis agent would provide
    input_data = {
        "data": {
            "analysis": "The analysis shows significant potential for AI.",
            "insights": ["AI can reduce diagnostic errors.", "Data privacy is a major hurdle."],
            "recommendations": ["Invest in secure data infrastructure.", "Develop clear regulatory frameworks."]
        },
        "context": {"goal": TEST_GOAL}
    }
    
    result = await synthesis.process(input_data)
    
    assert "data" in result
    assert "synthesized_output" in result["data"]
    assert "formatted_output" in result["data"]
    assert "formatted_text" in result["data"]["formatted_output"]
    assert len(result["data"]["synthesized_output"]) > 0
    assert result["status"] == "completed"

@pytest.mark.asyncio
async def test_full_system_orchestration():
    """Test the complete multi-agent system from goal to final output."""
    orchestrator = MultiAgentOrchestrator()
    
    result = await orchestrator.execute(TEST_GOAL)
    
    assert "final_output" in result
    assert "evaluation" in result
    assert "agent_order" in result
    assert len(result["agent_order"]) > 0
    
    evaluation = result["evaluation"]
    assert "goal_satisfaction" in evaluation
    assert evaluation["goal_satisfaction"] >= 0.0
    assert evaluation["goal_satisfaction"] <= 1.0
    
    final_output_data = result.get("final_output", {}).get("data", {})
    assert "synthesized_output" in final_output_data or "analysis" in final_output_data