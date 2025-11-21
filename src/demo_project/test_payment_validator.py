"""
Payment Validator Tests

Comprehensive test suite for the PaymentValidator class.
This will be executed by the Runtime to validate code changes.
"""

import os
import sys

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from decimal import Decimal

from payment_validator import (Currency, PaymentMethod, PaymentValidator,
                               ValidationError)


class TestPaymentValidator:
    """Test suite for PaymentValidator"""

    def setup_method(self):
        """Setup for each test"""
        self.validator = PaymentValidator()

    # ========================================================================
    # Amount Validation Tests
    # ========================================================================

    def test_validate_amount_valid_integer(self):
        """Test validation with valid integer amount"""
        assert self.validator.validate_amount(100) == True

    def test_validate_amount_valid_float(self):
        """Test validation with valid float amount"""
        assert self.validator.validate_amount(99.99) == True

    def test_validate_amount_valid_string(self):
        """Test validation with valid string amount"""
        assert self.validator.validate_amount("50.00") == True

    def test_validate_amount_valid_decimal(self):
        """Test validation with valid Decimal amount"""
        assert self.validator.validate_amount(Decimal("100.50")) == True

    def test_validate_amount_minimum(self):
        """Test validation with minimum amount"""
        assert self.validator.validate_amount(0.01) == True

    def test_validate_amount_below_minimum(self):
        """Test validation fails for amount below minimum"""
        with pytest.raises(ValidationError, match="at least"):
            self.validator.validate_amount(0.001)

    def test_validate_amount_maximum(self):
        """Test validation with maximum amount"""
        assert self.validator.validate_amount(999999.99) == True

    def test_validate_amount_above_maximum(self):
        """Test validation fails for amount above maximum"""
        with pytest.raises(ValidationError, match="cannot exceed"):
            self.validator.validate_amount(1000000.00)

    def test_validate_amount_too_many_decimals(self):
        """Test validation fails for too many decimal places"""
        with pytest.raises(ValidationError, match="decimal places"):
            self.validator.validate_amount(10.123)

    def test_validate_amount_none(self):
        """Test validation fails for None amount"""
        with pytest.raises(ValidationError, match="required"):
            self.validator.validate_amount(None)

    def test_validate_amount_invalid_format(self):
        """Test validation fails for invalid format"""
        with pytest.raises(ValidationError, match="Invalid amount format"):
            self.validator.validate_amount("invalid")

    # ========================================================================
    # Currency Validation Tests
    # ========================================================================

    def test_validate_currency_eur(self):
        """Test validation with EUR currency"""
        assert self.validator.validate_currency("EUR") == True

    def test_validate_currency_usd(self):
        """Test validation with USD currency"""
        assert self.validator.validate_currency("USD") == True

    def test_validate_currency_gbp(self):
        """Test validation with GBP currency"""
        assert self.validator.validate_currency("GBP") == True

    def test_validate_currency_invalid(self):
        """Test validation fails for invalid currency"""
        with pytest.raises(ValidationError, match="Invalid currency"):
            self.validator.validate_currency("XYZ")

    def test_validate_currency_none(self):
        """Test validation fails for None currency"""
        with pytest.raises(ValidationError, match="required"):
            self.validator.validate_currency(None)

    def test_validate_currency_empty_string(self):
        """Test validation fails for empty string"""
        with pytest.raises(ValidationError, match="required"):
            self.validator.validate_currency("")

    # ========================================================================
    # Payment Method Validation Tests
    # ========================================================================

    def test_validate_payment_method_credit_card(self):
        """Test validation with credit card"""
        assert self.validator.validate_payment_method("credit_card") == True

    def test_validate_payment_method_debit_card(self):
        """Test validation with debit card"""
        assert self.validator.validate_payment_method("debit_card") == True

    def test_validate_payment_method_bank_transfer(self):
        """Test validation with bank transfer"""
        assert self.validator.validate_payment_method("bank_transfer") == True

    def test_validate_payment_method_sepa(self):
        """Test validation with SEPA"""
        assert self.validator.validate_payment_method("sepa") == True

    def test_validate_payment_method_invalid(self):
        """Test validation fails for invalid payment method"""
        with pytest.raises(ValidationError, match="Invalid payment method"):
            self.validator.validate_payment_method("bitcoin")

    def test_validate_payment_method_none(self):
        """Test validation fails for None payment method"""
        with pytest.raises(ValidationError, match="required"):
            self.validator.validate_payment_method(None)

    # ========================================================================
    # Complete Payment Validation Tests
    # ========================================================================

    def test_validate_payment_complete_valid(self):
        """Test validation of complete valid payment"""
        payment = {"amount": 100.50, "currency": "EUR", "payment_method": "credit_card"}
        assert self.validator.validate_payment(payment) == True

    def test_validate_payment_missing_amount(self):
        """Test validation fails when amount is missing"""
        payment = {"currency": "EUR", "payment_method": "credit_card"}
        with pytest.raises(ValidationError, match="Amount"):
            self.validator.validate_payment(payment)

    def test_validate_payment_missing_currency(self):
        """Test validation fails when currency is missing"""
        payment = {"amount": 100.50, "payment_method": "credit_card"}
        with pytest.raises(ValidationError, match="Currency"):
            self.validator.validate_payment(payment)

    def test_validate_payment_missing_payment_method(self):
        """Test validation fails when payment method is missing"""
        payment = {"amount": 100.50, "currency": "EUR"}
        with pytest.raises(ValidationError, match="Payment method"):
            self.validator.validate_payment(payment)

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_validate_zero_amount(self):
        """Test validation fails for zero amount"""
        with pytest.raises(ValidationError, match="at least"):
            self.validator.validate_amount(0)

    def test_validate_negative_amount(self):
        """Test validation fails for negative amount"""
        with pytest.raises(ValidationError, match="at least"):
            self.validator.validate_amount(-10.00)


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])
