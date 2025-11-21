import json
from typing import List, Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)
from pydantic import BaseModel, Field

from src.agents.llms.hf_llm import HfLLM
from src.agents.orchestration.states import AgentState
from src.agents.prompts.researcher_prompt import \
    RESEARCHER_SYSTEM_PROMPT as researcher_prompt
from src.agents.tools.knowledge_api_tool import \
    KnowledgeAPISearchTool as KnowledgeAPITool
from src.config import settings
from src.logging_config import setup_logging

logger = setup_logging(
    service_name="researcher_agent", log_file="app.log", log_level="INFO"
)


class ResearchAgent:
    """Researcher Agent - queries Knowledge API using tools"""

    def __init__(self):
        # Initialize tools
        self.knowledge_tool = KnowledgeAPITool(api_url=None)

        # Initialize LLM
        hf_llm_instance = HfLLM()
        self.llm = hf_llm_instance.get_llm()
        self.researcher_llm = self.llm.bind_tools([self.knowledge_tool])

    def researcher_node(self, state: AgentState) -> AgentState:
        logger.info("Researcher Agent processing...")

        # Call LLM with tool
        messages = [SystemMessage(content=researcher_prompt)] + list(state["messages"])

        try:
            response = self.researcher_llm.invoke(messages)

            # If LLM wants to use tool, execute it
            if response.tool_calls:
                tool_call = response.tool_calls[0]
                logger.info(f"Researcher calling tool: {tool_call['name']}")

                # 1. Execute tool
                tool_result_dict = self.knowledge_tool._run(**tool_call["args"])
                # logger.info(f"Knowledge tool returned: {tool_result_dict}")

                # 2. For the ToolMessage, content MUST be a string.
                tool_result_string = json.dumps(tool_result_dict)

                # Create tool message
                from langchain_core.messages import ToolMessage

                tool_message = ToolMessage(
                    content=tool_result_string,  # Pass the string version here
                    tool_call_id=tool_call["id"],
                )

                # Get final response
                final_messages = messages + [response, tool_message]
                final_response = self.researcher_llm.invoke(final_messages)

                # check valid json
                if not self.is_valid_json(final_response.content):
                    # Retry once
                    final_response = self.researcher_llm.invoke(final_messages)

                # update the state
                state["messages"] = [response, tool_message, final_response]
                state["search_results"] = json.loads(final_response.content)

                logger.info("Researcher Agent completed with tool usage.")
                # logger.info(f"Final response: {state['messages'][-1].content}")
                logger.info(f"Final response: {state['search_results']}")

        except Exception as e:
            logger.error(f"Researcher Agent failed: {e}")

        return state

    def is_valid_json(self, json_string):
        """
        Check if a string is valid JSON.
        """
        try:
            json.loads(json_string)
            return True
        except (json.JSONDecodeError, TypeError, ValueError):
            return False
