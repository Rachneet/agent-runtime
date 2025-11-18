"""
Sample Knowledge Data

This simulates the content that would be in Riverty's Enterprise Knowledge Graph.
"""

from datetime import datetime, timedelta
from knowledge_graph import KnowledgeNode, SourceType


def get_sample_knowledge():
    """
    Get sample knowledge nodes that simulate Riverty's parsed repository data.
    
    This includes:
    - Service documentation from Confluence
    - Code structure from parsed repositories
    - Database schemas and documentation
    """
    
    now = datetime.now()
    
    return [
        # Payment Service Documentation
        KnowledgeNode(
            id="payment-service-overview",
            title="Payment Service Overview",
            content="""The Payment Service handles all payment processing for Riverty's payment platform.
            
Key Components:
- PaymentController: Main API endpoint handler
- PaymentValidator: Validates payment requests
- FraudDetectionClient: Integrates with fraud detection service
- PaymentProcessor: Core payment processing logic

Dependencies:
- fraud-detection-service (critical)
- notification-service (optional)
- postgres-db (critical)
- redis-cache (optional)

API Endpoints:
- POST /api/v1/payments - Process payment
- GET /api/v1/payments/{id} - Get payment status
- POST /api/v1/payments/{id}/refund - Refund payment

Recent Changes:
- 2024-11-10: Fixed timeout handling in PaymentProcessor
- 2024-11-08: Added validation for EU payments
- 2024-11-05: Optimized database queries for better performance
            """,
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/PAYMENTS/Overview",
            tags=["payment", "service", "api", "documentation"],
            updated_at=now - timedelta(days=5),
            metadata={"owner": "team-payments", "status": "active"}
        ),
        
        # Test Documentation
        KnowledgeNode(
            id="payment-service-tests",
            title="Payment Service Test Suite",
            content="""Test coverage for the Payment Service.

Test Files:
1. tests/unit/test_payment_validator.py (29 tests)
   - Tests payment validation logic
   - Location: demo_project/tests/unit/test_payment_validator.py
   - Tests: amount validation, currency validation, payment method validation
   - Coverage: 98%
   - Last modified: 2024-11-10 by john.doe
   
   Test Categories:
   - Amount validation (11 tests)
     * Valid amounts (integer, float, string, Decimal)
     * Boundary tests (min, max)
     * Invalid amounts (negative, zero, wrong format)
   
   - Currency validation (6 tests)
     * Valid currencies (EUR, USD, GBP)
     * Invalid currencies
     * Missing/empty currency
   
   - Payment method validation (6 tests)
     * Valid methods (credit_card, debit_card, bank_transfer, sepa)
     * Invalid methods
     * Missing method
   
   - Complete payment validation (4 tests)
     * Valid complete payments
     * Missing required fields
   
   - Edge cases (2 tests)
     * Zero and negative amounts

Running Tests:
```bash
# Run all tests
cd demo_project && pytest tests/unit/test_payment_validator.py -v

# Run specific test
pytest tests/unit/test_payment_validator.py::TestPaymentValidator::test_validate_amount_valid_integer -v

# Run with coverage
pytest tests/unit/test_payment_validator.py --cov=src --cov-report=term
```

CI/CD:
Tests run automatically on PR creation and merge to main.
All tests currently passing (35/35).
            """,
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/PAYMENTS/Testing",
            tags=["testing", "payment", "ci-cd", "unit-tests"],
            updated_at=now - timedelta(days=3),
            metadata={"owner": "team-payments", "test_count": 35, "location": "demo_project/tests/unit/test_payment_validator.py"}
        ),
        
        # Code Repository Info
        KnowledgeNode(
            id="payment-validator-code",
            title="PaymentValidator Class",
            content="""PaymentValidator class in payment-service repository.

Location: src/payment/validator.py

Class: PaymentValidator
- Methods:
  - validate_payment(payment_data: Dict) -> ValidationResult
  - validate_amount(amount: Decimal) -> bool
  - validate_currency(currency: str) -> bool
  - validate_payment_method(method: str) -> bool

Dependencies:
- ConfigLoader (from common.config)
- DatabaseClient (from common.database)
- PaymentRules (from payment.rules)

Used by 23 services across the platform:
- payment-api
- checkout-service
- subscription-service
- ... (20 more)

Recent changes:
- commit abc123: "Fix payment timeout handling" (2024-11-10)
  - Increased timeout from 5s to 10s
  - Added retry logic for transient failures
- commit def456: "Add validation for EU payments" (2024-11-08)
  - Added SEPA validation
  - Updated currency validation rules
            """,
            source_type=SourceType.CODE_REPOSITORY,
            source_url="https://github.com/riverty/payment-service/blob/main/src/payment/validator.py",
            tags=["code", "payment", "validator", "python"],
            updated_at=now - timedelta(days=6),
            metadata={
                "repository": "payment-service",
                "file_path": "src/payment/validator.py",
                "language": "python",
                "owner": "team-payments"
            }
        ),
        
        # Deployment Guide
        KnowledgeNode(
            id="deploy-user-service",
            title="Deploying User Service to Production",
            content="""How to deploy the User Service to production.

Prerequisites:
- Azure CLI configured
- kubectl access to production cluster
- Approval from team lead

Steps:
1. Create deployment PR with version bump
2. Wait for CI/CD pipeline to pass
3. Get approval from at least 2 team members
4. Merge to main branch
5. Automated deployment will trigger
6. Monitor deployment in Azure Portal

Rollback:
If issues are detected, run: ./scripts/rollback.sh user-service

Monitoring:
- Check Azure Application Insights for errors
- Monitor Grafana dashboards
- Check PagerDuty alerts

Recent deployments:
- 2024-11-12: v2.1.5 - Added OAuth2 support
- 2024-11-01: v2.1.4 - Bug fixes
            """,
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/DEPLOY/UserService",
            tags=["deployment", "production", "user-service"],
            updated_at=now - timedelta(days=10),
            metadata={"category": "deployment", "environment": "production"}
        ),
        
        # Database Schema
        KnowledgeNode(
            id="payments-db-schema",
            title="Payments Database Schema",
            content="""Database schema for the payments table.

Database: payments_db
Table: payments

Columns:
- id (UUID, PRIMARY KEY)
- user_id (UUID, FOREIGN KEY to users.id)
- amount (DECIMAL(10,2), NOT NULL)
- currency (VARCHAR(3), NOT NULL)
- status (ENUM: pending, processing, completed, failed)
- payment_method (VARCHAR(50))
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- metadata (JSONB)

Indexes:
- idx_user_id ON user_id
- idx_status ON status
- idx_created_at ON created_at

Recent migrations:
- 2024-11-05: Added metadata JSONB column
- 2024-10-20: Added payment_method column
            """,
            source_type=SourceType.DATABASE,
            source_url="https://confluence.riverty.com/display/DB/PaymentsSchema",
            tags=["database", "schema", "payments", "postgres"],
            updated_at=now - timedelta(days=12),
            metadata={"database": "payments_db", "table": "payments"}
        ),
        
        # Security Documentation
        KnowledgeNode(
            id="security-best-practices",
            title="Security Best Practices",
            content="""Security guidelines for Riverty services.

Authentication:
- All services must use OAuth 2.0
- Never store credentials in code
- Use Azure Key Vault for secrets

Authorization:
- Implement RBAC (Role-Based Access Control)
- Principle of least privilege
- Regular access reviews

Data Protection:
- Encrypt sensitive data at rest
- Use TLS 1.3 for data in transit
- PII must be encrypted and logged

Logging:
- Never log sensitive data (passwords, tokens, PII)
- Use structured logging (JSON format)
- Centralize logs in Azure Monitor

Incident Response:
- Report security incidents immediately to security@riverty.com
- Follow incident response playbook
            """,
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/SEC/BestPractices",
            tags=["security", "compliance", "best-practices"],
            updated_at=now - timedelta(days=20),
            metadata={"category": "security", "importance": "critical"}
        ),
        
        # Testing Best Practices
        KnowledgeNode(
            id="testing-standards",
            title="Testing Standards and Guidelines",
            content="""Testing standards for all Riverty services.

Test Pyramid:
- 70% Unit tests (fast, isolated)
- 20% Integration tests (test component interactions)
- 10% E2E tests (full user workflows)

Coverage Requirements:
- Minimum 80% code coverage
- 100% coverage for critical paths (payment, authentication)

Test Naming:
Use descriptive names: test_should_reject_invalid_payment_amount()

CI/CD Integration:
- All tests run on PR creation
- E2E tests run nightly
- Performance tests run weekly

Common Issues:
- Flaky tests: Usually due to timing or external dependencies
- Slow tests: Consider mocking external services
            """,
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/QA/Standards",
            tags=["testing", "quality", "ci-cd", "standards"],
            updated_at=now - timedelta(days=15),
            metadata={"category": "testing", "owner": "team-qa"}
        ),
        
        # Service Dependencies
        KnowledgeNode(
            id="service-dependency-graph",
            title="Service Dependency Graph",
            content="""Dependencies between Riverty services.

Critical Dependencies:
- payment-service depends on:
  → fraud-detection-service (critical)
  → notification-service (optional)
  → postgres-db (critical)
  → redis-cache (optional)

- checkout-service depends on:
  → payment-service (critical)
  → inventory-service (critical)
  → user-service (critical)

- fraud-detection-service depends on:
  → ml-model-service (critical)
  → postgres-db (critical)

Services that depend on payment-service:
← checkout-service
← subscription-service
← reporting-service
← admin-portal

Impact Analysis:
If payment-service is down:
- checkout-service cannot process orders
- subscription-service cannot process renewals
- reporting-service cannot generate payment reports
            """,
            source_type=SourceType.CONFLUENCE,
            source_url="https://confluence.riverty.com/display/ARCH/Dependencies",
            tags=["architecture", "dependencies", "services"],
            updated_at=now - timedelta(days=7),
            metadata={"category": "architecture"}
        ),
    ]