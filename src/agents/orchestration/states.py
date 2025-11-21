from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """
    Shared state that all agents read from and write to.
    This is how agents communicate and coordinate.
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    task_description: str

    # Researcher Agent writes these
    search_results: dict

    # Extractor Agent
    extraction_results: dict

    # Executor Agent writes these
    execution_results: dict

    # Final response
    final_answer: str
