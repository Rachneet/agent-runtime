"""
Sample Knowledge Data - ROBUST VERSION

This simulates Riverty's Knowledge Graph.
It attempts to read real files from disk, but falls back to hardcoded 
strings to ensure the demo works perfectly regardless of file paths.
"""

from datetime import datetime, timedelta
from pathlib import Path
import os

# --- 1. Helper to read files or provide fallback ---
def read_demo_file(filename):
    """
    Reads file from disk or returns hardcoded fallback content.
    """
    # Try to find the file in common locations
    potential_paths = [
        Path("src/demo_project") / filename,
        Path("demo_project") / filename,
        Path("../src/demo_project") / filename,
        Path("agents/demo_project") / filename
    ]
    
    for path in potential_paths:
        try:
            if path.exists():
                return path.read_text(encoding='utf-8')
        except Exception:
            continue
            
    # --- FALLBACKS (Guarantees the Demo Works) ---
    print(f"⚠️  File {filename} not found on disk. Using FALLBACK content.")
    
    if filename == "payment_validator.py":
        return """from decimal import Decimal
from typing import Any, Dict, Optional

class ValidationError(Exception):
    pass

class PaymentValidator:
    def validate_amount(self, amount: Any) -> bool:
        if amount is None: raise ValidationError("Amount is required")
        try: val = float(amount)
        except: raise ValidationError("Invalid amount format")
        if val < 0.01: raise ValidationError("Amount must be at least 0.01")
        if val > 999999.99: raise ValidationError("Amount cannot exceed 1,000,000")
        return True

    def validate_currency(self, currency: Any) -> bool:
        if not currency: raise ValidationError("Currency is required")
        if currency not in ["EUR", "USD", "GBP"]: raise ValidationError("Invalid currency")
        return True

    def validate_payment_method(self, method: Any) -> bool:
        if not method: raise ValidationError("Payment method is required")
        if method not in ["credit_card", "debit_card", "bank_transfer", "sepa"]:
            raise ValidationError("Invalid payment method")
        return True

    def validate_payment(self, payment: Dict) -> bool:
        self.validate_amount(payment.get("amount"))
        self.validate_currency(payment.get("currency"))
        self.validate_payment_method(payment.get("payment_method"))
        return True
"""
    elif filename == "test_payment_validator.py":
        return """import pytest
import sys
import os

# Handle imports dynamically for the container environment
try:
    from demo_project.payment_validator import PaymentValidator, ValidationError
except ImportError:
    try:
        from src.demo_project.payment_validator import PaymentValidator, ValidationError
    except ImportError:
        from payment_validator import PaymentValidator, ValidationError

class TestPaymentValidator:
    def setup_method(self):
        self.validator = PaymentValidator()
    
    def test_validate_amount_valid_integer(self):
        assert self.validator.validate_amount(100) == True
    
    def test_validate_amount_minimum(self):
        assert self.validator.validate_amount(0.01) == True

    def test_validate_currency_eur(self):
        assert self.validator.validate_currency("EUR") == True

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
"""
    return ""


# --- 2. Main Data Function ---
def get_sample_knowledge():
    """
    Get sample knowledge nodes for the simulation.
    """
    # Import locally to avoid circular dependency issues during init
    try:
        from src.knowledge_api.knowledge_graph import KnowledgeNode, SourceType
    except ImportError:
        from knowledge_graph import KnowledgeNode, SourceType
    
    now = datetime.now()
    
    # Get content (either from disk or fallback)
    test_content = read_demo_file("test_payment_validator.py")
    source_content = read_demo_file("payment_validator.py")
    
    return [
        # --- Node 1: Test File ---
        KnowledgeNode(
            id="payment-service-tests",
            title="Payment Service Test Suite",
            content=f"""Test coverage for the Payment Service.
Running: pytest demo_project/test_payment_validator.py
""",
            source_type=SourceType.CODE_REPOSITORY,
            source_url="github.com/riverty/payment-service/tests/test_payment_validator.py",
            tags=["testing", "payment", "pytest", "unit-tests", "test"],
            updated_at=now - timedelta(days=1),
            metadata={
                "test_file_path": "demo_project/test_payment_validator.py",
                "source_file_path": "demo_project/payment_validator.py",
                "test_command": "pytest demo_project/test_payment_validator.py -v",
                "dependencies": ["pytest"],
                # The tool uses this for the initial file
                "file_content": test_content
            }
        ),
        
        # --- Node 2: Source Code (The one that was missing content!) ---
        KnowledgeNode(
            id="payment-validator-code",
            # Title MUST match the filename for the tool's search to find it
            title="payment_validator.py", 
            content=f"""Payment Validator implementation logic.
Location: demo_project/payment_validator.py
""",
            source_type=SourceType.CODE_REPOSITORY,
            source_url="github.com/riverty/payment-service/src/payment_validator.py",
            tags=["code", "payment", "validator", "python"],
            updated_at=now - timedelta(days=1),
            metadata={
                "file_path": "demo_project/payment_validator.py",
                "language": "python",
                # CRITICAL FIX: The tool looks for 'full_content' in metadata
                "full_content": source_content 
            }
        ),
        
        # --- Node 3: Confluence Doc (Filler) ---
        KnowledgeNode(
            id="testing-standards",
            title="Testing Standards",
            content="Riverty requires 80% code coverage.",
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/QA",
            tags=["standards"],
            updated_at=now - timedelta(days=10)
        )
    ]