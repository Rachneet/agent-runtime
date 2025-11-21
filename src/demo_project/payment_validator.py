"""
Payment Validator

This is a realistic payment validation module that the tests will validate.
"""

from decimal import Decimal
from enum import Enum
from typing import Dict, Optional


class Currency(Enum):
    """Supported currencies"""

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"


class PaymentMethod(Enum):
    """Supported payment methods"""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    SEPA = "sepa"


class ValidationError(Exception):
    """Raised when validation fails"""

    pass


class PaymentValidator:
    """
    Validates payment requests.

    This is the core validation logic for Riverty's payment service.
    """

    def __init__(self, timeout: int = 5):
        """
        Initialize validator.

        Args:
            timeout: Timeout for validation (seconds)
        """
        self.timeout = timeout
        self.min_amount = Decimal("0.01")
        self.max_amount = Decimal("999999.99")

    def validate_payment(self, payment_data: Dict) -> bool:
        """
        Validate a complete payment request.

        Args:
            payment_data: Payment data dictionary

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        # Validate all fields
        self.validate_amount(payment_data.get("amount"))
        self.validate_currency(payment_data.get("currency"))
        self.validate_payment_method(payment_data.get("payment_method"))

        return True

    def validate_amount(self, amount) -> bool:
        """
        Validate payment amount.

        Args:
            amount: Payment amount (can be string, int, float, or Decimal)

        Returns:
            True if valid

        Raises:
            ValidationError: If amount is invalid
        """
        if amount is None:
            raise ValidationError("Amount is required")

        try:
            amount_decimal = Decimal(str(amount))
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid amount format: {amount}")

        if amount_decimal < self.min_amount:
            raise ValidationError(f"Amount must be at least {self.min_amount}")

        if amount_decimal > self.max_amount:
            raise ValidationError(f"Amount cannot exceed {self.max_amount}")

        # Check decimal places (max 2)
        if amount_decimal.as_tuple().exponent < -2:
            raise ValidationError("Amount cannot have more than 2 decimal places")

        return True

    def validate_currency(self, currency: str) -> bool:
        """
        Validate currency code.

        Args:
            currency: ISO currency code

        Returns:
            True if valid

        Raises:
            ValidationError: If currency is invalid
        """
        if not currency:
            raise ValidationError("Currency is required")

        try:
            Currency(currency)
        except ValueError:
            valid_currencies = [c.value for c in Currency]
            raise ValidationError(
                f"Invalid currency: {currency}. "
                f"Must be one of: {', '.join(valid_currencies)}"
            )

        return True

    def validate_payment_method(self, method: str) -> bool:
        """
        Validate payment method.

        Args:
            method: Payment method identifier

        Returns:
            True if valid

        Raises:
            ValidationError: If method is invalid
        """
        if not method:
            raise ValidationError("Payment method is required")

        try:
            PaymentMethod(method)
        except ValueError:
            valid_methods = [m.value for m in PaymentMethod]
            raise ValidationError(
                f"Invalid payment method: {method}. "
                f"Must be one of: {', '.join(valid_methods)}"
            )

        return True
