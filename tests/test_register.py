"""
Tests for the CashRegister class.
"""

import pytest
from decimal import Decimal
from src.register import CashRegister
from src.exceptions import NegativePriceError


class TestCashRegister:
    """Test suite for the CashRegister class."""
    
    def test_cumulative_total(self):
        """Test that the cumulative total is correctly calculated."""
        register = CashRegister()
        
        # Add multiple items
        register.scan_item("APPLE", Decimal("2.50"), 3)  # 7.50
        register.scan_item("BREAD", Decimal("1.80"), 2)  # 3.60
        register.scan_item("MILK", Decimal("3.20"), 1)   # 3.20
        
        # The total should be 7.50 + 3.60 + 3.20 = 14.30
        expected_total = Decimal("14.30")
        assert register.total() == expected_total
    
    def test_reset_clears_register(self):
        """Test that reset completely clears the register."""
        register = CashRegister()
        
        # Add items
        register.scan_item("APPLE", Decimal("2.50"), 3)
        register.scan_item("BREAD", Decimal("1.80"), 2)
        
        # Verify that the total is not zero
        assert register.total() > Decimal("0")
        
        # Reset to zero
        register.reset()
        
        # Verify that the total is now zero
        assert register.total() == Decimal("0")
    
    def test_negative_price_raises_exception(self):
        """Test that a negative or zero price raises a NegativePriceError."""
        register = CashRegister()
        
        # Test with negative price
        with pytest.raises(NegativePriceError):
            register.scan_item("INVALID", Decimal("-1.00"))
        
        # Test with zero price
        with pytest.raises(NegativePriceError):
            register.scan_item("INVALID", Decimal("0.00"))
        
        # Test with negative price and quantity
        with pytest.raises(NegativePriceError):
            register.scan_item("INVALID", Decimal("-2.50"), 3)
        
        # Verify that a positive price does not raise an exception
        try:
            register.scan_item("VALID", Decimal("1.00"))
        except NegativePriceError:
            pytest.fail("A positive price should not raise an exception") 