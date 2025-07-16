from decimal import Decimal
from typing import Dict, List
from .exceptions import NegativePriceError, DiscountError
from .models import LineItem, Receipt


class CashRegister:
    """
    A simple cash register to scan items, calculate the total, and reset.

    Attributes:
        _line_items (List[LineItem]): Internal list to track all scanned line items.
        _discount_percent (Decimal): Current discount percentage (0-100).
    """

    def __init__(self):
        """Initialize an empty cash register."""
        self._line_items: List[LineItem] = []
        self._discount_percent: Decimal = Decimal("0")

    def scan_item(self, sku: str, price: Decimal, qty: int = 1):
        """
        Add one or more units of an item to the register.

        Args:
            sku (str): The stock-keeping unit (product code).
            price (Decimal): Price of a single unit.
            qty (int): Number of units to add (default is 1).

        Raises:
            NegativePriceError: If the price is zero or negative.
        """
        if price <= 0:
            raise NegativePriceError(price)
        
        line_item = LineItem(sku=sku, qty=qty, unit_price=price)
        self._line_items.append(line_item)

    def apply_discount(self, percent: Decimal) -> None:
        """
        Apply a discount percentage to the total.

        Args:
            percent (Decimal): Discount percentage (must be strictly between 0 and 100).

        Raises:
            DiscountError: If the percentage is not strictly between 0 and 100.
        """
        if percent <= 0 or percent >= 100:
            raise DiscountError(percent)
        
        self._discount_percent = percent

    def remove_discount(self) -> None:
        """
        Remove the current discount.

        Resets the discount percentage to 0.
        """
        self._discount_percent = Decimal("0")

    def total(self) -> Decimal:
        """
        Compute the total amount for all scanned items, applying any discount.

        Returns:
            Decimal: The total cost of all items scanned so far, with discount applied.
        """
        subtotal = sum(item.total_price for item in self._line_items)
        if self._discount_percent > 0:
            discount_amount = subtotal * (self._discount_percent / 100)
            return subtotal - discount_amount
        return subtotal

    def reset(self) -> None:
        """
        Clear all items from the register.

        Resets the register to its initial empty state.
        """
        self._line_items.clear()

    def to_receipt(self) -> Receipt:
        """
        Generate a receipt from the current register state.
        
        Consolidates line items with the same SKU and unit_price.
        
        Returns:
            Receipt: A receipt containing consolidated line items and totals.
        """
        # Group line items by (sku, unit_price) to consolidate identical items
        consolidated_items: Dict[tuple, LineItem] = {}
        
        for item in self._line_items:
            key = (item.sku, item.unit_price)
            if key in consolidated_items:
                # Add quantity to existing item
                consolidated_items[key].qty += item.qty
            else:
                # Create new consolidated item
                consolidated_items[key] = LineItem(
                    sku=item.sku,
                    qty=item.qty,
                    unit_price=item.unit_price
                )
        
        # Convert to list and sort by SKU for consistent ordering
        lines = sorted(consolidated_items.values(), key=lambda x: x.sku)
        
        # Calculate totals
        total_gross = sum(item.total_price for item in lines)
        discount_amount = total_gross * (self._discount_percent / 100) if self._discount_percent > 0 else Decimal("0")
        total_due = total_gross - discount_amount
        
        return Receipt(
            lines=lines,
            total_gross=total_gross,
            discount_pct=self._discount_percent,
            total_due=total_due
        )
