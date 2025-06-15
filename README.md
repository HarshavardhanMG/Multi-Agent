Of course. Based on the provided code and your detailed requirements, here is a comprehensive and professionally formatted README file.

Modular Multi-Agent AI System

![alt text](https://img.shields.io/badge/License-MIT-yellow.svg)

A sophisticated multi-agent AI system designed to achieve complex user goals through a dynamic and modular chain of specialized agents. This system uses a Planner Agent to interpret a goal and route it through a sequence of enrichment agents (Research, Analysis, Synthesis), each progressively adding value to the data until a comprehensive final output is generated.

The project demonstrates advanced concepts including agent chaining, dynamic routing, data enrichment, and iterative refinement.

Core Features

Modular Agent Architecture: Each agent (Planner, Research, Analysis, Synthesis) is a self-contained module with a specific responsibility.

Dynamic Planning & Routing: The Planner Agent analyzes the user's goal to create a custom execution plan and determines the optimal sequence of agents to run.

Intelligent Data Enrichment: Data flows from one agent to the next, with each step adding more context, structure, and insight.

Iterative Refinement: Agents can loop on their current task if their output confidence is below a set threshold, ensuring higher quality results.

Targeted & General Research: The Research Agent can perform general-purpose research using an LLM or execute targeted API calls for specific queries (e.g., finding SpaceX launch data).

Built-in Evaluation: The system self-evaluates its final output against the original goal for a measurable score of success.

System Flow & Architecture

The system operates on a pipeline model orchestrated by main.py. The flow is designed for clarity, traceability, and robust error handling.

+-------------+      +------------------+      +--------------------+      +--------------------+      +---------------------+      +----------------+
| User Goal   |----->|   PlannerAgent   |----->|   ResearchAgent    |----->|   AnalysisAgent    |----->|   SynthesisAgent    |----->|  Final Output  |
+-------------+      +------------------+      +--------------------+      +--------------------+      +---------------------+      +----------------+
      |                      | (Creates Plan &     | (Gathers raw data,     | (Structures data,    | (Creates a human-    |
      |                      |  Agent Order)      |  e.g., via APIs)       |  finds insights)     |  readable report)    |
      `-----------------------------------------------------------------------------------------------------------------------> (Context Passed Through)


Planning: The PlannerAgent receives the user's goal. It uses a powerful language model (Google's Gemini) to generate a step-by-step plan and a corresponding agent_order list (e.g., ["research", "analysis", "synthesis"]).

Execution: The orchestrator iterates through the agent_order.

Data Enrichment: The output of one agent becomes the direct input for the next. The central data object is continuously enriched as it moves through the pipeline.

Context Preservation: The original goal and other key context are passed along with the data, ensuring every agent stays aligned with the primary objective.

Synthesis: The SynthesisAgent receives the fully enriched data and generates the final, comprehensive report.

Agent Logic

Each agent is a specialized worker contributing to the overall goal.

PlannerAgent:

Input: High-level user goal.

Logic: Uses an LLM to create a structured JSON object containing a natural language plan and a list of agents to execute in sequence.

Output: A data structure containing the plan and the agent execution order.

ResearchAgent:

Input: The plan and goal.

Logic:

If the goal is specific (e.g., "SpaceX launch"), it executes a targeted function (get_spacex_launch) that calls external APIs (RocketLaunch.Live, OpenWeatherMap).

For general goals, it uses the LLM to conduct research based on the plan.

Output: A research summary and the raw source data it collected.

AnalysisAgent:

Input: The research summary and source data.

Logic: Prompts an LLM to act as a data analyst. It parses the unstructured research text to extract key insights and actionable recommendations, structuring them into a JSON object.

Output: The original data, now enriched with structured analysis, insights, and recommendations.

SynthesisAgent:

Input: The fully analyzed and enriched data package.

Logic: Uses an LLM to combine all the information—summaries, insights, and recommendations—into a final, well-structured, and coherent report for the end-user.

Output: The final formatted text.

APIs & Technologies

Core Language: Python 3.9+

AI/LLM: Google Generative AI (Gemini 1.5 Flash)

Asynchronous Operations: asyncio and aiohttp for non-blocking API calls.

External Data APIs:

RocketLaunch.Live: https://fdo.rocketlaunch.live/json/... - Used to get data on upcoming rocket launches.

OpenWeatherMap: https://api.openweathermap.org/data/2.5 - Used to get weather data for a given set of coordinates.

Configuration: pydantic-settings for managing API keys and settings via a .env file.

Testing: pytest and pytest-asyncio for unit and integration testing of the agents.

Setup & Installation

Clone the Repository

git clone <your-repo-url>
cd <your-repo-directory>
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Install Dependencies

pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Create Environment File
Create a file named .env in the root of the project directory and add your API keys:

# Get your key from Google AI Studio
GOOGLE_API_KEY="your_google_api_key_here"

# Get your key from OpenWeatherMap
OPENWEATHER_API_KEY="your_openweathermap_api_key_here"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Env
IGNORE_WHEN_COPYING_END
Usage

Run the system from the command line by providing a goal. The system will print the execution flow and the final results.

python main.py --goal "Your goal here"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Example:

python main.py --goal "Find the next SpaceX launch, check the weather at that location, and summarize if it may be delayed."
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
Evaluation Framework

The system's effectiveness is evaluated on several axes to ensure reliability and quality.

Goal Satisfaction Score: The PlannerAgent includes an evaluate_goal_satisfaction method that uses the LLM to score the final output against the original goal on a scale of 0.0 to 1.0. This provides a quantitative measure of success.

Agent Trajectory & Data Enrichment: The history of each agent is tracked. By inspecting the input and output of each step in the history, we can evaluate how effectively the data was enriched and transformed as it passed through the agent chain.

Planning and Routing Logic: The initial plan and agent_order generated by the PlannerAgent can be evaluated for correctness and efficiency. Did it choose the right agents? Was the order logical for the given goal?

Code Quality and Testing: The codebase adheres to modern standards with type hints and a modular structure. The tests/ directory contains unit and integration tests written with pytest to validate the logic of individual agents and the orchestration of the full system.

Project Structure
.
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── planner.py
│   ├── research_agent.py
│   ├── analysis_agent.py
│   └── synthesis_agent.py
├── utils/
│   ├── __init__.py
│   ├── api_helpers.py
│   └── config.py
├── tests/
│   └── test_agents.py
├── .env.example
├── main.py
├── requirements.txt
└── README.md
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
License

This project is licensed under the MIT License. See the LICENSE file for details.