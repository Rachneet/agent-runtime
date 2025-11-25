import re
import warnings
from typing import Dict

from dotenv import load_dotenv
from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from src.agents.agents.docker_runtime_client import DockerRuntimeClient
from src.agents.agents.extraction_agent import CodeExtractionAgent
from src.agents.agents.reporting_agent import ReportingAgent
from src.agents.agents.researcher_agent import ResearchAgent
from src.agents.orchestration.states import AgentState
from src.logging_config import setup_logging

# Suppress the UUID v7 warning
warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

load_dotenv()


logger = setup_logging(service_name="workflow", log_file="app.log", log_level="INFO")


class AgentWorkflow:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.extractor = CodeExtractionAgent()
        self.runtime_client = DockerRuntimeClient()
        self.reporter = ReportingAgent()

        self.compiled_workflow = self.build_workflow()

    def should_run_code(self, state: AgentState) -> str:
        """
        Router: Checks if the Task Agent prepared a job.
        """
        files = state["extraction_results"].get("files")
        command = state["extraction_results"].get("command")

        # Robust check: Must be 'execute' AND have a command
        if files and command:
            logger.info(f"Routing to 'runtime'.")
            return "runtime"

        logger.info(f"Issue in research. Routing to 'researcher'.")
        return "researcher"

    def build_workflow(self):
        """Create and compile the multi-agent workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("researcher", self.researcher.researcher_node)
        workflow.add_node("extractor", self.extractor.extraction_node)
        workflow.add_node("runtime", self.runtime_client.runtime_node)
        workflow.add_node("reporter", self.reporter.reporter_node)

        # Define edges
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "extractor")

        # conditional router
        workflow.add_conditional_edges(
            "extractor",
            self.should_run_code,  # Use new router function
            {"runtime": "runtime", "researcher": "researcher"},
        )

        workflow.add_edge("runtime", "reporter")
        workflow.add_edge("reporter", END)
        return workflow.compile()

    def full_pipeline(self, task: str):
        """Run the full workflow given a task description."""
        try:
            initial_state = {
                "messages": [HumanMessage(content=task)],
                "task_description": task,
                "next_agent": "researcher",
                "search_results": {},
                "execution_results": {},
                "final_answer": "",
            }

            result = self.compiled_workflow.invoke(initial_state)
            logger.info("Workflow execution completed successfully.")
            # logger.info(result)
            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    # Helper method
    def save_workflow(self, file_path: str):
        """
        Save the agent workflow graph in the specified directory
        """
        data = self.compiled_workflow.get_graph().draw_mermaid_png()

        try:
            with open(file_path, "wb") as f:
                f.write(data)
        except Exception as e:
            print("Unexpected error in saving file: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("Riverty Multi-Agent System - Test")
    print("=" * 70)
    print("\n!!! MAKE SURE THE DOCKER RUNTIME SERVICE IS RUNNING ON PORT 8001 !!!\n")

    agent_workflow = AgentWorkflow()
    # agent_workflow.view_workflow()
    run_agent_workflow = agent_workflow.full_pipeline
    query = "Locate the source code and test files for the payment service. Once identified, execute the specific test suite for those files and report the results."
    query2 = "Tell me about the CEO of Google."
    query3 = (
        "Find the payment service tests and the source code, and run flake8 on them."
    )
    query4 = "What is the capital of France?"
    result = run_agent_workflow(query)

    print("\n" + "=" * 70)
    print("Workflow Complete!")
    print("=" * 70)
    print(f"\nExecution Results: {result.get('execution_results', {})}")
    print(f"\nFinal Answer:\n{result.get('final_answer', 'No answer provided.')}")
