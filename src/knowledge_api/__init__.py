"""
Riverty Knowledge API - Simulated Knowledge Graph

This package provides a simulated version of Riverty's unified knowledge API.
"""

from .knowledge_api_client import KnowledgeAPIClient
from .knowledge_graph import KnowledgeGraph, KnowledgeNode, SourceType

__all__ = ["KnowledgeNode", "SourceType", "KnowledgeGraph", "KnowledgeAPIClient"]

__version__ = "1.0.0"
