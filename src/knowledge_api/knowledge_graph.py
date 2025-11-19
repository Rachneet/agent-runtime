"""
Riverty Knowledge Graph - IMPROVED SEARCH

Better search algorithm that handles:
- Multi-word queries
- Relevance scoring
- Partial matches
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import re


class SourceType(Enum):
    """Types of knowledge sources"""
    CONFLUENCE = "confluence"
    CODE_REPOSITORY = "code_repository"
    DATABASE = "database"


@dataclass
class KnowledgeNode:
    """
    A node in the knowledge graph representing a piece of knowledge.
    """
    id: str
    title: str
    content: str
    source_type: SourceType
    source_url: str
    tags: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """
    Simulated knowledge graph with IMPROVED search.
    """
    
    def __init__(self):
        self.nodes: List[KnowledgeNode] = []
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample knowledge"""
        from src.knowledge_api.sample_data import get_sample_knowledge
        self.nodes = get_sample_knowledge()
    
    def _calculate_relevance_score(self, node: KnowledgeNode, query_terms: List[str]) -> float:
        """
        Calculate relevance score for a node based on query terms.
        Higher score = more relevant.
        """
        score = 0.0
        
        title_lower = node.title.lower()
        content_lower = node.content.lower()
        tags_lower = [tag.lower() for tag in node.tags]
        
        for term in query_terms:
            term_lower = term.lower()
            
            # Exact title match (highest weight)
            if term_lower == title_lower:
                score += 100.0
            # Term in title (high weight)
            elif term_lower in title_lower:
                score += 50.0
            
            # Exact tag match (high weight)
            if term_lower in tags_lower:
                score += 40.0
            # Partial tag match
            elif any(term_lower in tag for tag in tags_lower):
                score += 20.0
            
            # Term in content (lower weight, but still counts)
            content_count = content_lower.count(term_lower)
            if content_count > 0:
                # More mentions = higher score, but with diminishing returns
                score += min(content_count * 5.0, 30.0)
            
            # Boost for metadata matches
            if 'metadata' in node.__dict__ and node.metadata:
                metadata_str = str(node.metadata).lower()
                if term_lower in metadata_str:
                    score += 15.0
        
        # Boost for multiple matching terms (query coherence)
        matching_terms = sum(1 for term in query_terms 
                           if term.lower() in title_lower 
                           or term.lower() in content_lower
                           or any(term.lower() in tag for tag in tags_lower))
        
        if matching_terms > 1:
            score += matching_terms * 10.0
        
        return score
    
    def search(
        self,
        query: str,
        source_types: Optional[List[SourceType]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 1
    ) -> List[KnowledgeNode]:
        """
        IMPROVED search that handles multi-word queries and ranks by relevance.
        
        Examples:
        - "payment test" → matches nodes with both "payment" AND "test"
        - "payment" → matches nodes with "payment" anywhere
        - "test validation" → ranks nodes by how well they match
        """
        
        # Split query into terms (handles multi-word queries)
        query_terms = [term.strip() for term in query.split() if term.strip()]
        
        if not query_terms:
            return []
        
        # Score all nodes
        scored_nodes = []
        
        for node in self.nodes:
            # Apply filters first
            if source_types and node.source_type not in source_types:
                continue
            
            if tags and not any(tag in node.tags for tag in tags):
                continue
            
            # Calculate relevance score
            score = self._calculate_relevance_score(node, query_terms)
            
            # Only include if score > 0 (at least one term matched)
            if score > 0:
                scored_nodes.append((score, node))
        
        # Sort by score (highest first)
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        
        # Return top results (without scores)
        return [node for score, node in scored_nodes[:limit]]


# Global knowledge graph instance
_knowledge_graph: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get the global knowledge graph instance"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph


# Test the improved search
if __name__ == "__main__":
    print("Testing Knowledge Graph Search\n")
    
    kg = get_knowledge_graph()
    
    # Test different queries
    test_queries = [
        "Run unit tests for payment service and report the results.",
        "Lint the payment service codebase.",
        "test",
        "payment validation",
        "pytest",
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        results = kg.search(query, limit=3)
        print(f"  Found {len(results)} results:")
        for node in results:
            print(f"    - {node.title}")
        print()