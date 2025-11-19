from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.llms.hf_llm import HfLLM
from src.agents.orchestration.states import AgentState
from src.logging_config import setup_logging
from src.agents.prompts.reporter_prompt import REPORTING_PROMPT    

logger = setup_logging(
    service_name="reporting_agent", 
    log_file="app.log", 
    log_level="INFO"
)

class ReportingAgent:
    def __init__(self):
        hf_llm_instance = HfLLM()
        self.llm = hf_llm_instance.get_llm()

    def reporter_node(self, state: AgentState) -> AgentState:
        logger.info("Reporting Agent processing...")
        
        # 1. Gather Context
        task = state.get("task_description")
        job_details = state.get("extraction_results")
        job_command = job_details["command"]

        execution_results = state.get("execution_results", {})
        
        # Scenario: Code Execution
        success = execution_results.get("success", False)
        exit_code = execution_results.get("exit_code", "Unknown")
        stdout = execution_results.get("stdout", "").strip()
        stderr = execution_results.get("stderr", "").strip()
        
        # If stdout is empty, check if we have a specific error message
        if not stdout and not stderr and "error" in execution_results:
                stderr = execution_results["error"]
        
        context = f"""
        USER TASK: {task}
        
        --- EXECUTION REPORT ---
        Command Run: {job_command}
        Status: {'Success' if success else 'Failure'} (Exit Code: {exit_code})
        
        --- STANDARD OUTPUT ---
        {stdout if stdout else "[No Output]"}
        
        --- ERROR LOGS ---
        {stderr if stderr else "[No Errors]"}
        """

        # 3. Call LLM
        messages = [
            SystemMessage(content=REPORTING_PROMPT),
            HumanMessage(content=context)
        ]
        
        response = self.llm.invoke(messages)
        state["messages"] = [response]
        state["final_answer"] = response.content
        
        # 4. Return updated state
        return state