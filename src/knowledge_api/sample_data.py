"""
Sample Knowledge Data

This simulates Riverty's Knowledge Graph.
It attempts to provide realistic sample data for testing the Knowledge API.
It includes knowledge from code repositories and Confluence.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path


def get_sample_knowledge():
    """
    Get sample knowledge nodes for the simulation.
    """

    try:
        from src.knowledge_api.knowledge_graph import KnowledgeNode, SourceType
    except ImportError:
        from knowledge_graph import KnowledgeNode, SourceType

    now = datetime.now()

    return [
        # --- Node 1: Code Repository ---
        KnowledgeNode(
            id="payment-validator-code",
            title="Payment Service: Payment Validator Logic (Python)",
            # CONCISE SUMMARY/SNIPPET for quick graph search filtering
            content="Core Python logic for transaction validation, ensuring amounts are positive and currency is supported (EUR, USD, GBP). Raises ValueError on failure.",
            source_type=SourceType.CODE_REPOSITORY,
            source_url="local/simulate/payment-service/src/payment_validator.py",  # Local/Azure/GitHub Path
            tags=["code", "payment", "python", "core-logic", "microservice"],
            updated_at=now - timedelta(days=2),
            metadata={
                "file_path": "src/demo_project/payment_validator.py",
                "language": "python",
                "class_names": ["PaymentValidator"],
                "method_signatures": [
                    "validate_transaction(amount: float, currency: str)"
                ],
                "related_ids": ["payment-service-tests", "testing-standards"],
            },
        ),
        # --- Node 2: Unit Test Suite (The Verification Index) ---
        KnowledgeNode(
            id="payment-service-tests",
            title="Unit Tests: Payment Validator Coverage",
            # CONCISE SUMMARY of what the test covers
            content="Pytest suite covering happy path for supported currencies and assertion of ValueError for non-positive amounts and unsupported currencies.",
            source_type=SourceType.CODE_REPOSITORY,
            source_url="local/simulate/payment-service/tests/test_payment_validator.py",  # Local/Azure/GitHub Path
            tags=["testing", "qa", "pytest", "unit-tests"],
            updated_at=now - timedelta(days=1),
            metadata={
                "file_path": "src/demo_project/test_payment_validator.py",
                "language": "python",
                "related_ids": ["payment-validator-code"],  # Explicit relationship
                "execution_command": "pytest src/demo_project/test_payment_validator.py -v",  # Agent action data
            },
        ),
        # --- Node 3: Confluence Document (The Policy Index) ---
        KnowledgeNode(
            id="testing-standards",
            title="QA Engineering Standards: Code Coverage Policy",
            # CONCISE SUMMARY of the document's key points
            content="Riverty requires 80% code coverage for all microservices. Payment validation is a critical path requiring 100% branch coverage.",
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/QA/Standards-V2",  # Confluence URL
            tags=["standards", "policy", "compliance", "qa"],
            updated_at=now - timedelta(days=30),
            metadata={
                "space_key": "QA",
                "document_author": "Jane Doe",
                "applies_to_ids": [
                    "payment-validator-code"
                ],  # Relationship back to the code
            },
        ),
        # --- Node 4: Database Schema (The Structure Index) ---
        KnowledgeNode(
            id="payment-db-schema",
            title="Payment Database Schema: Transactions Table DDL",
            # CONCISE SUMMARY of the structure
            content="PostgreSQL DDL for the 'transactions' table, includes columns for amount (DECIMAL), currency (VARCHAR), and status check constraint.",
            source_type=SourceType.DATABASE,
            source_url="internal-db/payments/schema/transactions.sql",  # Internal DB location
            tags=["database", "sql", "schema", "postgres"],
            updated_at=now - timedelta(days=60),
            metadata={
                "engine": "PostgreSQL",
                "primary_table": "transactions",
                "schema_version": "1.2.0",
            },
        ),
    ]
