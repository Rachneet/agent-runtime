"""
Riverty Knowledge API Client

This is the client library that agents use to query the knowledge graph.
In production, this would connect to the actual unified knowledge API.
"""

from typing import List, Optional, Dict, Any
from src.knowledge_api.knowledge_graph import SourceType, KnowledgeNode, KnowledgeGraph


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
        limit: int = 1
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
            query=query,
            source_types=source_types,
            tags=tags,
            limit=limit
        )
        
        # Format results
        return {
            "query": query,
            "total_results": len(nodes),
            "results": [self._format_node(node) for node in nodes],
            "sources_searched": sources or ["all"]
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
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        node = self.knowledge_graph.get_by_id(document_id)
        if node:
            return self._format_node(node)
        return None

    def get_by_tags(self, tags: List[str], limit: int = 1) -> Dict[str, Any]:
        """Get documents by tags."""
        nodes = self.knowledge_graph.get_by_tags(tags, limit)
        return {
            "tags": tags,
            "total_results": len(nodes),
            "results": [self._format_node(node) for node in nodes]
        }
    
    def get_recent(self, limit: int = 1) -> Dict[str, Any]:
        """Get recently updated documents."""
        nodes = self.knowledge_graph.get_recent(limit)
        return {
            "total_results": len(nodes),
            "results": [self._format_node(node) for node in nodes]
        }
    
    def _format_node(self, node: KnowledgeNode) -> Dict[str, Any]:
        """Format a knowledge node for API response."""
        return {
            "id": node.id,
            "title": node.title,
            "excerpt": self._create_excerpt(node.content),
            "full_content": node.content,
            "source": {
                "type": node.source_type.value,
                "url": node.source_url
            },
            "tags": node.tags,
            "updated_at": node.updated_at.isoformat(),
            "metadata": node.metadata
        }
    
    def _create_excerpt(self, content: str, max_length: int = 200) -> str:
        """Create an excerpt from content."""
        if len(content) <= max_length:
            return content
        
        excerpt = content[:max_length]
        last_period = excerpt.rfind('.')
        last_newline = excerpt.rfind('\n')
        
        break_point = max(last_period, last_newline)
        if break_point > max_length // 2:
            excerpt = excerpt[:break_point + 1]
        
        return excerpt.strip() + "..."



# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Riverty Knowledge API - Demo")
    print("=" * 70)
    
    # Create client
    client = KnowledgeAPIClient()
    
    # Example 1: Search for deployment info
    print("\n1. Searching for 'Test files for payment service'...")
    results = client.search("Test files for payment service", limit=3)
    print(f"   Found {results['total_results']} results:")
    for result in results['results']:
        print(f"   - {result['title']} ({result['source']['type']})")
    
    # Example 2: Search Confluence only
    print("\n2. Searching Confluence for 'testing'...")
    results = client.search_confluence("testing")
    print(f"   Found {results['total_results']} results:")
    for result in results['results']:
        print(f"   - {result['title']}")
    
    # Example 3: Search by tags
    print("\n3. Getting documents tagged with 'security'...")
    results = client.get_by_tags(["security"])
    print(f"   Found {results['total_results']} results:")
    for result in results['results']:
        print(f"   - {result['title']}")
    
    # Example 4: Get specific document
    print("\n4. Getting specific document...")
    doc = client.get_document("deploy-user-service")
    if doc:
        print(f"   Title: {doc['title']}")
        print(f"   Source: {doc['source']['url']}")
        print(f"   Excerpt: {doc['excerpt'][:100]}...")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
