"""
Tests for the CashRegister class.
"""

from decimal import Decimal

import pytest

from src.exceptions import DiscountError, NegativePriceError
from src.models import LineItem, Receipt
from src.register import CashRegister


class TestLineItem:
    """Test suite for the LineItem dataclass."""

    def test_line_item_creation(self):
        """Test basic LineItem creation."""
        item = LineItem(sku="APPLE", qty=3, unit_price=Decimal("2.50"))

        assert item.sku == "APPLE"
        assert item.qty == 3
        assert item.unit_price == Decimal("2.50")

    def test_line_item_total_price(self):
        """Test total_price property calculation."""
        item = LineItem(sku="BREAD", qty=2, unit_price=Decimal("1.80"))

        expected_total = Decimal("3.60")  # 2 * 1.80
        assert item.total_price == expected_total

    def test_line_item_total_price_single_item(self):
        """Test total_price for single item."""
        item = LineItem(sku="MILK", qty=1, unit_price=Decimal("3.20"))

        assert item.total_price == Decimal("3.20")

    def test_line_item_total_price_precision(self):
        """Test total_price maintains decimal precision."""
        item = LineItem(sku="ITEM", qty=3, unit_price=Decimal("33.33"))

        expected_total = Decimal("99.99")  # 3 * 33.33
        assert item.total_price == expected_total


class TestReceipt:
    """Test suite for the Receipt dataclass."""

    def test_receipt_creation(self):
        """Test basic Receipt creation."""
        lines = [
            LineItem(sku="APPLE", qty=3, unit_price=Decimal("2.50")),
            LineItem(sku="BREAD", qty=2, unit_price=Decimal("1.80")),
        ]

        receipt = Receipt(
            lines=lines,
            total_gross=Decimal("11.10"),
            discount_pct=Decimal("10"),
            total_due=Decimal("9.99"),
        )

        assert len(receipt.lines) == 2
        assert receipt.total_gross == Decimal("11.10")
        assert receipt.discount_pct == Decimal("10")
        assert receipt.total_due == Decimal("9.99")

    def test_receipt_empty_lines(self):
        """Test Receipt with empty lines."""
        receipt = Receipt(
            lines=[],
            total_gross=Decimal("0.00"),
            discount_pct=Decimal("0"),
            total_due=Decimal("0.00"),
        )

        assert len(receipt.lines) == 0
        assert receipt.total_gross == Decimal("0.00")
        assert receipt.total_due == Decimal("0.00")


class TestCashRegister:
    """Test suite for the CashRegister class."""

    def test_cumulative_total(self):
        """Test that the cumulative total is correctly calculated."""
        register = CashRegister()

        # Add multiple items
        register.scan_item("APPLE", Decimal("2.50"), 3)  # 7.50
        register.scan_item("BREAD", Decimal("1.80"), 2)  # 3.60
        register.scan_item("MILK", Decimal("3.20"), 1)  # 3.20

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
        """Test that apply_discount raises DiscountError for invalid
        percentages."""
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


class TestCashRegisterReceipt:
    """Test suite for the CashRegister receipt functionality."""

    def test_to_receipt_basic(self):
        """Test basic to_receipt functionality."""
        register = CashRegister()

        # Add items
        register.scan_item("APPLE", Decimal("2.50"), 3)
        register.scan_item("BREAD", Decimal("1.80"), 2)

        # Generate receipt
        receipt = register.to_receipt()

        # Verify receipt structure
        assert isinstance(receipt, Receipt)
        assert len(receipt.lines) == 2

        # Verify line items (sorted by SKU)
        apple_line = receipt.lines[0]  # APPLE comes first alphabetically
        bread_line = receipt.lines[1]  # BREAD comes second

        assert apple_line.sku == "APPLE"
        assert apple_line.qty == 3
        assert apple_line.unit_price == Decimal("2.50")
        assert apple_line.total_price == Decimal("7.50")

        assert bread_line.sku == "BREAD"
        assert bread_line.qty == 2
        assert bread_line.unit_price == Decimal("1.80")
        assert bread_line.total_price == Decimal("3.60")

        # Verify totals
        assert receipt.total_gross == Decimal("11.10")  # 7.50 + 3.60
        assert receipt.discount_pct == Decimal("0")
        assert receipt.total_due == Decimal("11.10")

    def test_to_receipt_with_consolidation(self):
        """Test to_receipt with consolidation of identical items."""
        register = CashRegister()

        # Add same SKU multiple times with same price
        register.scan_item("APPLE", Decimal("2.50"), 3)  # First scan
        register.scan_item("BREAD", Decimal("1.80"), 2)  # Different item
        register.scan_item("APPLE", Decimal("2.50"), 2)  # Same SKU, same price

        # Generate receipt
        receipt = register.to_receipt()

        # Should have 2 lines (consolidated)
        assert len(receipt.lines) == 2

        # Find apple line
        apple_line = next(line for line in receipt.lines if line.sku == "APPLE")
        bread_line = next(line for line in receipt.lines if line.sku == "BREAD")

        # Apple should be consolidated: 3 + 2 = 5
        assert apple_line.qty == 5
        assert apple_line.unit_price == Decimal("2.50")
        assert apple_line.total_price == Decimal("12.50")  # 5 * 2.50

        # Bread should remain unchanged
        assert bread_line.qty == 2
        assert bread_line.unit_price == Decimal("1.80")
        assert bread_line.total_price == Decimal("3.60")

        # Verify totals
        assert receipt.total_gross == Decimal("16.10")  # 12.50 + 3.60
        assert receipt.total_due == Decimal("16.10")

    def test_to_receipt_different_prices_no_consolidation(self):
        """Test that items with same SKU but different prices are not
        consolidated."""
        register = CashRegister()

        # Add same SKU with different prices
        register.scan_item("APPLE", Decimal("2.50"), 3)  # Regular price
        register.scan_item("APPLE", Decimal("3.00"), 1)  # Premium price

        # Generate receipt
        receipt = register.to_receipt()

        # Should have 2 lines (not consolidated due to different prices)
        assert len(receipt.lines) == 2

        # Both lines should be for APPLE but with different prices
        apple_lines = [line for line in receipt.lines if line.sku == "APPLE"]
        assert len(apple_lines) == 2

        # Sort by price to have consistent ordering
        apple_lines.sort(key=lambda x: x.unit_price)

        # First line: 3 apples at 2.50
        assert apple_lines[0].qty == 3
        assert apple_lines[0].unit_price == Decimal("2.50")
        assert apple_lines[0].total_price == Decimal("7.50")

        # Second line: 1 apple at 3.00
        assert apple_lines[1].qty == 1
        assert apple_lines[1].unit_price == Decimal("3.00")
        assert apple_lines[1].total_price == Decimal("3.00")

        # Verify totals
        assert receipt.total_gross == Decimal("10.50")  # 7.50 + 3.00
        assert receipt.total_due == Decimal("10.50")

    def test_to_receipt_with_discount(self):
        """Test to_receipt with discount applied."""
        register = CashRegister()

        # Add items
        register.scan_item("ITEM1", Decimal("100.00"), 1)
        register.scan_item("ITEM2", Decimal("50.00"), 1)

        # Apply 20% discount
        register.apply_discount(Decimal("20"))

        # Generate receipt
        receipt = register.to_receipt()

        # Verify totals
        assert receipt.total_gross == Decimal("150.00")  # 100 + 50
        assert receipt.discount_pct == Decimal("20")
        assert receipt.total_due == Decimal("120.00")  # 150 - 20% = 120

    def test_to_receipt_discount_precision(self):
        """Test receipt discount calculation precision."""
        register = CashRegister()

        # Add items with total that creates decimal precision
        register.scan_item("ITEM1", Decimal("33.33"), 1)

        # Apply 10% discount
        register.apply_discount(Decimal("10"))

        # Generate receipt
        receipt = register.to_receipt()

        # Verify precision
        assert receipt.total_gross == Decimal("33.33")
        assert receipt.discount_pct == Decimal("10")
        assert receipt.total_due == Decimal("29.997")  # 33.33 - 10% = 29.997

    def test_to_receipt_empty_register(self):
        """Test to_receipt with empty register."""
        register = CashRegister()

        # Generate receipt without scanning items
        receipt = register.to_receipt()

        # Verify empty receipt
        assert len(receipt.lines) == 0
        assert receipt.total_gross == Decimal("0.00")
        assert receipt.discount_pct == Decimal("0")
        assert receipt.total_due == Decimal("0.00")

    def test_to_receipt_complex_scenario(self):
        """Test complex scenario with multiple items, consolidation, and
        discount."""
        register = CashRegister()

        # Complex scanning scenario
        register.scan_item("APPLE", Decimal("2.50"), 3)  # 7.50
        register.scan_item("BREAD", Decimal("1.80"), 2)  # 3.60
        register.scan_item("APPLE", Decimal("2.50"), 2)  # 5.00 (will
        # consolidate)
        register.scan_item("MILK", Decimal("3.20"), 1)  # 3.20
        register.scan_item(
            "APPLE", Decimal("3.00"), 1
        )  # 3.00 (different price, no consolidation)
        register.scan_item("BREAD", Decimal("1.80"), 1)  # 1.80 (will
        # consolidate)

        # Apply 15% discount
        register.apply_discount(Decimal("15"))

        # Generate receipt
        receipt = register.to_receipt()

        # Verify lines count (should be 4: consolidated APPLE@2.50,
        # BREAD@1.80, MILK@3.20, APPLE@3.00)
        assert len(receipt.lines) == 4

        # Find each line
        apple_250_line = next(
            line
            for line in receipt.lines
            if line.sku == "APPLE" and line.unit_price == Decimal("2.50")
        )
        apple_300_line = next(
            line
            for line in receipt.lines
            if line.sku == "APPLE" and line.unit_price == Decimal("3.00")
        )
        bread_line = next(line for line in receipt.lines if line.sku == "BREAD")
        milk_line = next(line for line in receipt.lines if line.sku == "MILK")

        # Verify consolidation
        assert apple_250_line.qty == 5  # 3 + 2 = 5
        assert apple_250_line.total_price == Decimal("12.50")  # 5 * 2.50

        assert apple_300_line.qty == 1
        assert apple_300_line.total_price == Decimal("3.00")

        assert bread_line.qty == 3  # 2 + 1 = 3
        assert bread_line.total_price == Decimal("5.40")  # 3 * 1.80

        assert milk_line.qty == 1
        assert milk_line.total_price == Decimal("3.20")

        # Verify totals
        expected_gross = Decimal("24.10")  # 12.50 + 3.00 + 5.40 + 3.20
        expected_due = Decimal("20.485")  # 24.10 - 15% = 20.485

        assert receipt.total_gross == expected_gross
        assert receipt.discount_pct == Decimal("15")
        assert receipt.total_due == expected_due

    def test_to_receipt_after_reset(self):
        """Test that to_receipt works correctly after reset."""
        register = CashRegister()

        # Add items and generate receipt
        register.scan_item("ITEM1", Decimal("10.00"), 1)
        receipt1 = register.to_receipt()
        assert len(receipt1.lines) == 1

        # Reset and add different items
        register.reset()
        register.scan_item("ITEM2", Decimal("20.00"), 1)
        receipt2 = register.to_receipt()

        # New receipt should only have new items
        assert len(receipt2.lines) == 1
        assert receipt2.lines[0].sku == "ITEM2"
        assert receipt2.total_gross == Decimal("20.00")
