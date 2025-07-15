"""
Tests for the CashRegister class.
"""

import pytest
from decimal import Decimal
from src.register import CashRegister
from src.exceptions import NegativePriceError, DiscountError


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
    
    def test_apply_discount_valid_percentage(self):
        """Test that apply_discount works with valid percentages."""
        register = CashRegister()
        
        # Add items with total of 100.00
        register.scan_item("ITEM1", Decimal("50.00"), 1)
        register.scan_item("ITEM2", Decimal("50.00"), 1)
        
        # Apply 10% discount
        register.apply_discount(Decimal("10"))
        
        # Total should be 90.00 (100.00 - 10%)
        expected_total = Decimal("90.00")
        assert register.total() == expected_total
    
    def test_apply_discount_invalid_percentage(self):
        """Test that apply_discount raises DiscountError for invalid percentages."""
        register = CashRegister()
        
        # Test with 0% (should raise exception)
        with pytest.raises(DiscountError):
            register.apply_discount(Decimal("0"))
        
        # Test with 100% (should raise exception)
        with pytest.raises(DiscountError):
            register.apply_discount(Decimal("100"))
        
        # Test with negative percentage
        with pytest.raises(DiscountError):
            register.apply_discount(Decimal("-10"))
        
        # Test with percentage > 100
        with pytest.raises(DiscountError):
            register.apply_discount(Decimal("150"))
    
    def test_remove_discount(self):
        """Test that remove_discount correctly removes the discount."""
        register = CashRegister()
        
        # Add items
        register.scan_item("ITEM1", Decimal("100.00"), 1)
        
        # Apply discount
        register.apply_discount(Decimal("20"))
        
        # Total should be 80.00 (100.00 - 20%)
        assert register.total() == Decimal("80.00")
        
        # Remove discount
        register.remove_discount()
        
        # Total should be back to 100.00
        assert register.total() == Decimal("100.00")
    
    def test_discount_precision(self):
        """Test that discount calculations maintain proper precision."""
        register = CashRegister()
        
        # Add items with total of 33.33
        register.scan_item("ITEM1", Decimal("33.33"), 1)
        
        # Apply 10% discount
        register.apply_discount(Decimal("10"))
        
        # Total should be 29.997 rounded to 29.997
        expected_total = Decimal("29.997")
        assert register.total() == expected_total
    
    def test_no_discount_by_default(self):
        """Test that no discount is applied by default."""
        register = CashRegister()
        
        # Add items
        register.scan_item("ITEM1", Decimal("50.00"), 1)
        
        # Total should be the same as item price (no discount)
        assert register.total() == Decimal("50.00")
    
    def test_reset_preserves_discount(self):
        """Test that reset clears items but preserves the discount."""
        register = CashRegister()
        
        # Add items
        register.scan_item("ITEM1", Decimal("100.00"), 1)
        
        # Apply discount
        register.apply_discount(Decimal("20"))
        
        # Verify discount is applied
        assert register.total() == Decimal("80.00")
        
        # Reset items
        register.reset()
        
        # Total should be zero but discount should still be present
        assert register.total() == Decimal("0.00")
        
        # Add new items to verify discount is still active
        register.scan_item("ITEM2", Decimal("50.00"), 1)
        
        # Total should be 40.00 (50.00 - 20%)
        assert register.total() == Decimal("40.00") 