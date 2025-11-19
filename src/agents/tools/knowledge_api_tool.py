from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, List, Dict, Any, Literal
import sys
import os

from src.logging_config import setup_logging

# try:
from src.knowledge_api.knowledge_api_client import KnowledgeAPIClient
# except ImportError:
#     from knowledge_api_client import KnowledgeAPIClient

logger = setup_logging(service_name="knowledge_search_tool", log_file="app.log", log_level="INFO")


# Input for the tool from the LLM
class KnowledgeSearchInput(BaseModel):
    query: str = Field(description="Search query for finding relevant documentation, code, or data")
    sources: List[Literal["confluence", "code_repository", "database"]] = Field(
        default=None,
        description=(
            "Specific sources to search. "
            "You MUST use one of these exact values: "
            "'confluence', 'code_repository', or 'database'. "
            "Do not use abbreviations like 'code' or 'docs'."
        )
    )

# Output schema
class KnowledgeSearchResultItem(BaseModel):
    """Structured data for a single relevant knowledge artifact."""
    id: str = Field(description="The stable ID of the knowledge node.")
    title: str = Field(description="The title of the document or file.")
    source_type: str = Field(description="The source category (e.g., 'code_repository', 'confluence').")

    file_path: Optional[str] = Field(description="The relative file path or key (e.g., 'src/validator.py', 'QA/Standards').")

    execution_command: Optional[str] = Field(
        default=None,
        description="The exact command to run this artifact (e.g., 'pytest path/to/file'). Only present for executable code/tests."
    )

    # Summary of content for LLM reasoning, not the full content
    content_summary: str = Field(description="A short summary of the file/document's content for context.")

    # The URL to the external system for deep linking
    source_url: str = Field(description="The full URL to the original source.")


class KnowledgeSearchOutput(BaseModel):
    """The full structured output of the search tool."""
    results: List[KnowledgeSearchResultItem] = Field(
        description="A list of relevant, structured knowledge artifacts found."
    )
    message: str = Field(description="A summary message about the search result.")


class KnowledgeAPISearchTool(BaseTool):
    name: str = "search_knowledge_api"
    description: str = "Use this tool to search Riverty's unified knowledge base for documentation, code, and data."
    args_schema: type[BaseModel] = KnowledgeSearchInput
    
    api_url: Optional[str] = None
    _client: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = KnowledgeAPIClient(api_url=self.api_url)
    
    def _run(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        limit: int = 3 
    ) -> Dict[str, Any]:
        
        logger.info(f"Tool searching for: query='{query}' (limit={limit})")
        
        results = self._client.search(
            query=query,
            sources=sources,
            limit=limit
        )
        
        return self._extract_structured_data(results)
    
    def _extract_structured_data(self, api_results: dict) -> Dict[str, Any]:
        """
        Extracts structured data from the API results, ensuring consistency
        for LLM consumption.
        """
        parsed_results = []
        raw_results = api_results.get('results', [])
        
        if not raw_results:
            return {
                "results": [],
                "message": "No relevant artifacts found in the knowledge base."
            }

        for res in raw_results:
            metadata = res.get('metadata', {})
            
            # 1. Get the path, favoring specific paths over generic ones
            path = metadata.get('file_path') or metadata.get('document_key')
            
            # 2. Extract the action command (will be None if not a test/code)
            command = metadata.get('execution_command')

            # 3. Use the node's main content field as the summary
            summary = res.get('content', 'No content summary available.')
            
            # Construct the structured item
            item = KnowledgeSearchResultItem(
                id=res.get('id', 'N/A'),
                title=res.get('title', 'Untitled Artifact'),
                source_type=res.get('source_type', 'unknown'),
                file_path=path,
                execution_command=command,
                content_summary=summary,
                source_url=res.get('source_url', 'N/A')
            )
            parsed_results.append(item.model_dump()) # Use model_dump to get a clean dict
            
        return {
            "results": parsed_results,
            "message": f"Successfully retrieved {len(parsed_results)} relevant artifacts."
        }
    