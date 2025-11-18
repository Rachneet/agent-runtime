from typing import Dict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from src.agents.orchestration.states import AgentState
from src.agents.agents.researcher_agent import ResearchAgent
from src.agents.agents.coordinator_agent import CoordinatorAgent

from src.agents.tools.docker_runtime_client import DockerRuntimeClient

from src.logging_config import setup_logging
import re

logger = setup_logging(
    service_name="workflow",
    log_file="app.log",
    log_level="INFO"
)

class AgentWorkflow:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.runtime_client = DockerRuntimeClient() 
        self.coordinator = CoordinatorAgent()

        self.compiled_workflow = self.build_workflow()
    
    # It's just a function, not a full agent class
    def runtime_node(self, state: AgentState) -> Dict:
        """
        Takes the files from the researcher and sends them
        to the Docker Runtime Service for execution.
        """
        logger.info("RUNTIME NODE: Preparing job for execution.")
        search_results = state.get("search_results")
        
        # 1. Extract files and command from search results
        files_to_run = []
        command = ""
        
        # Add test file
        test_file = search_results.get("test_file")
        if test_file:
            files_to_run.append({
                "filename": test_file["filename"],
                "content": self._extract_code_from_content(test_file["content"])
            })
            command = self._clean_command(test_file.get("command", ""))
            
        # Add source files (This is the critical part you were missing)
        for source_file in search_results.get("source_files", []):
            content = source_file.get("content", "")
            if content and content.strip(): # Only add if content exists
                files_to_run.append({
                    "filename": source_file["filename"],
                    "content": self._extract_code_from_content(content)
                })
        
        logger.info(f"Extracted {len(files_to_run)} file(s). Command: {command}")

        # 2. Call the runtime client
        execution_results = self.runtime_client._run(
            command=command,
            files=files_to_run
        )
        logger.info("RUNTIME NODE: Execution completed.")

        # 3. Parse and log results
        stdout = execution_results.get('stdout', '')
        stderr = execution_results.get('stderr', '')
        
        if execution_results.get("success"):
            logger.info("RUNTIME NODE: Execution successful.")
            # Try to parse pytest results
            passed = re.search(r'(\d+)\s+passed', stdout)
            failed = re.search(r'(\d+)\s+failed', stdout)
            final_answer = (
                f"Execution successful (Exit Code 0).\n"
                f"Passed: {passed.group(1) if passed else 'N/A'}\n"
                f"Failed: {failed.group(1) if failed else 'N/A'}\n\n"
                f"--- RAW OUTPUT ---\n{stdout}"
            )
        else:
            logger.warning("RUNTIME NODE: Execution failed.")
            final_answer = f"Execution failed.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

        return {
            "execution_results": execution_results,
            "final_answer": final_answer
        }

    # Router function
    def should_run_code(self, state: AgentState) -> str:
        """
        Router: Decides if we have code to run
        or if we should just end.
        """
        logger.info("ROUTER: Checking if code should be run.")
        search_results = state.get("search_results")
        
        if search_results and search_results.get("found"):
            logger.info("ROUTER: Code found. Routing to 'runtime' node.")
            return "runtime"
        else:
            logger.info("ROUTER: No code found. Routing to 'end'.")
            return "end"

    def build_workflow(self):
        """Create and compile the multi-agent workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("researcher", self.researcher.researcher_node)
        workflow.add_node("runtime", self.runtime_node) 
        workflow.add_node("coordinator", self.coordinator.coordinator_node)

        # Define edges
        workflow.set_entry_point("researcher")
        
        # NEW conditional router
        workflow.add_conditional_edges(
            "researcher",
            self.should_run_code, # Use new router function
            {
                "runtime": "runtime",
                "end": END
            }
        )

        workflow.add_edge("runtime", "coordinator")
        workflow.add_edge("coordinator", END)
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
                "final_answer": ""
            }

            result = self.compiled_workflow.invoke(initial_state)
            logger.info("Workflow execution completed successfully.")
            return result
        
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    # Helper method
    def _extract_code_from_content(self, content: str) -> str:
        if "**Complete Test File Content:**" in content:
            parts = content.split("**Complete Test File Content:**")
            if len(parts) > 1:
                content = parts[1]
        
        match = re.search(r'```(python|bash|)\s*\n(.*?)```', content, re.DOTALL)
        if match:
            return match.group(2).strip()
        return content.strip().replace("```", "")
    
    def _clean_command(self, command: str) -> str:
        return self._extract_code_from_content(command)


if __name__ == "__main__":
    print("=" * 70)
    print("Riverty Multi-Agent System - Test")
    print("=" * 70)
    print("\n!!! MAKE SURE THE DOCKER RUNTIME SERVICE IS RUNNING ON PORT 8001 !!!\n")
    
    agent_workflow = AgentWorkflow()
    run_agent_workflow = agent_workflow.full_pipeline
    query = "Find test files for the payment service and run them"
    query2 = "tell me about Google."
    result = run_agent_workflow(query2)

    print("\n" + "=" * 70)
    print("Workflow Complete!")
    print("=" * 70)
    print(f"\nExecution Results: {result.get('execution_results', {}).get('success')}")
    print(f"\nFinal Answer:\n{result.get('final_answer', 'No answer provided.')}")
    