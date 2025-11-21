"""
Riverty Knowledge API Client

This is the client library that agents use to query the knowledge graph.
In production, this would connect to the actual unified knowledge API.
"""

from typing import Any, Dict, List, Optional

from src.knowledge_api.knowledge_graph import (KnowledgeGraph, KnowledgeNode,
                                               SourceType)


class KnowledgeAPIClient:
    """
    Client for querying Riverty's unified knowledge API.

    In production, this would make HTTP requests to the actual API.
    For now, it queries our simulated knowledge graph.
    """

    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the knowledge API client.

        Args:
            api_url: URL of the knowledge API (unused in simulation)
        """
        # if there is no api_url provided, use default
        self.api_url = api_url or "https://knowledge-api.riverty.com"
        # Initialize knowledge graph (simulated)
        self.knowledge_graph = KnowledgeGraph()

    def search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 1,
    ) -> Dict[str, Any]:
        """
        Search across all knowledge sources.

        Args:
            query: Search query
            sources: Filter by source types (confluence, code_repository, database)
            tags: Filter by tags
            limit: Maximum results

        Returns:
            Dictionary with search results
        """
        # Convert source strings to SourceType enums
        source_types = None
        if sources:
            source_types = [SourceType(s) for s in sources]

        # Perform search
        nodes = self.knowledge_graph.search(
            query=query, source_types=source_types, tags=tags, limit=limit
        )

        # Format results
        return {
            "query": query,
            "total_results": len(nodes),
            "results": [self._format_node(node) for node in nodes],
            "sources_searched": sources or ["all"],
        }

    def search_confluence(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search only Confluence documentation."""
        return self.search(query=query, sources=["confluence"], limit=limit)

    def search_code(self, query: str, limit: int = 1) -> Dict[str, Any]:
        """Search code repositories."""
        return self.search(query=query, sources=["code_repository"], limit=limit)

    def search_database(self, query: str, limit: int = 1) -> Dict[str, Any]:
        """Search database schemas and documentation."""
        return self.search(query=query, sources=["database"], limit=limit)

    def _format_node(self, node: KnowledgeNode) -> Dict[str, Any]:
        """Format a knowledge node for API response."""
        return {
            "id": node.id,
            "title": node.title,
            "content": node.content,
            "source": {"type": node.source_type.value, "url": node.source_url},
            "tags": node.tags,
            "updated_at": node.updated_at.isoformat(),
            "metadata": node.metadata,
        }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Riverty Knowledge API - Demo")
    print("=" * 70)

    # Create client
    client = KnowledgeAPIClient()

    # Example 1: Search for deployment info
    print("\n1. Searching for 'Test files for payment service'...")
    results = client.search(
        "Run unit tests for payment service and report the results.",
        sources=["code_repository"],
        limit=3,
    )
    print(f"   Found {results['total_results']} results:")
    for result in results["results"]:
        print(f"   - {result['title']} ({result['source']['type']})")

    # Example 2: Search Confluence only
    print("\n2. Searching Confluence for 'testing'...")
    results = client.search_confluence("testing")
    print(f"   Found {results['total_results']} results:")
    for result in results["results"]:
        print(f"   - {result['title']}")

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
