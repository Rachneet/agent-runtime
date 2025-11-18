from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.llms.hf_llm import HfLLM
from src.agents.orchestration.states import AgentState
from src.logging_config import setup_logging
from src.agents.prompts.coordinator_prompt import COORDINATOR_PROMPT    

logger = setup_logging(
    service_name="coordinator_agent", 
    log_file="app.log", 
    log_level="INFO"
)

class CoordinatorAgent:
    def __init__(self):
        hf_llm_instance = HfLLM()
        self.llm = hf_llm_instance.get_llm()

    def coordinator_node(self, state: AgentState) -> AgentState:
        logger.info("Coordinator Agent processing...")
        
        # 1. Gather Context
        task = state.get("task_description")
        execution_results = state.get("execution_results", {})
        
        # Format the execution data for the LLM
        success = execution_results.get("success", False)
        exit_code = execution_results.get("exit_code", "Unknown")
        stdout = execution_results.get("stdout", "No output")
        stderr = execution_results.get("stderr", "No errors")
        
        context = f"""
        ORIGINAL TASK: {task}
        
        EXECUTION STATUS: {'Success' if success else 'Failure'}
        EXIT CODE: {exit_code}
        
        LOGS:
        {stdout}
        {stderr}
        """

        # 2. Call LLM
        messages = [
            SystemMessage(content=COORDINATOR_PROMPT),
            HumanMessage(content=context)
        ]
        
        response = self.llm.invoke(messages)
        
        # 3. Return Final Answer
        return {
            "final_answer": response.content,
            "messages": [response], # Add to history
            "next_agent": "end"
        }