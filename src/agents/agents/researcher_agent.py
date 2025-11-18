from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_huggingface import ChatHuggingFace
from src.config import settings
from src.agents.llms.hf_llm import HfLLM
from src.agents.tools.knowledge_api_tool import KnowledgeAPISearchTool as KnowledgeAPITool
from src.agents.prompts.researcher_prompt import RESEARCHER_SYSTEM_PROMPT as researcher_prompt
from src.agents.orchestration.states import AgentState
from src.logging_config import setup_logging

from typing import Literal
import json


logger = setup_logging(
    service_name="researcher_agent", 
    log_file="app.log", 
    log_level="INFO"
)


class ResearchAgent:
    """Researcher Agent - queries Knowledge API using tools"""
    def __init__(self):
        # Initialize tools
        self.knowledge_tool = KnowledgeAPITool(api_url=None)

        # Initialize LLM
        hf_llm_instance = HfLLM()
        llm = hf_llm_instance.get_llm()
        self.researcher_llm = llm.bind_tools([self.knowledge_tool])

    # Define agent nodes
    def researcher_node(self, state: AgentState) -> AgentState:
        """Researcher Agent node - queries Knowledge API"""
        logger.info("Researcher Agent processing...")

        # Prepare messages with system prompt
        messages = [SystemMessage(content=researcher_prompt)] + list(state["messages"])
            
        try:
            # Call LLM with tool
            response = self.researcher_llm.invoke(messages)
            
            # If LLM wants to use tool, execute it
            if response.tool_calls:
                tool_call = response.tool_calls[0]
                logger.info(f"Researcher calling tool: {tool_call['name']}")
                
                # 1. Execute tool
                tool_result_dict = self.knowledge_tool._run(**tool_call['args'])
                # logger.info(f"Knowledge tool returned: {tool_result_dict}")
                
                # 2. For the ToolMessage, content MUST be a string.
                tool_result_string = json.dumps(tool_result_dict)
            
                # Create tool message
                from langchain_core.messages import ToolMessage
                tool_message = ToolMessage(
                    content=tool_result_string, # Pass the string version here
                    tool_call_id=tool_call['id']
                )
                
                # Get final response
                final_messages = messages + [response, tool_message]
                final_response = self.researcher_llm.invoke(final_messages)

                return {
                    "messages": [response, tool_message, final_response],
                    "search_results": tool_result_dict,
                    "next_agent": "executor",
                    "final_response": final_response.content
                }
            else:
                logger.info("SUCCESS: Researcher did NOT use tool, setting next_agent='executor'")
                return {
                    "messages": [response],
                    "search_results": {"status": "no_tool_used"},
                    "next_agent": "executor",
                    "final_response": response.content
                }
        except Exception as e:
            logger.error(f"Researcher agent error: {e}", exc_info=True) 
            error_msg = AIMessage(content=f"Error in research: {str(e)}")
            logger.warning("FAILURE: Researcher hit exception, setting next_agent='end'")
            return {
                "messages": [error_msg],
                "search_results": {"status": "error", "error": str(e)},
                "next_agent": "end"
            }
        