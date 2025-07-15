from decimal import Decimal
from typing import Dict
from .exceptions import NegativePriceError, DiscountError


class CashRegister:
    """
    A simple cash register to scan items, calculate the total, and reset.

    Attributes:
        _items (Dict[str, Decimal]): Internal dictionary to track item totals by SKU.
        _discount_percent (Decimal): Current discount percentage (0-100).
    """

    def __init__(self):
        """Initialize an empty cash register."""
        self._items: Dict[str, Decimal] = {}
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
        
        total_price = price * qty
        self._items[sku] = self._items.get(sku, Decimal("0.00")) + total_price

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
        subtotal = sum(self._items.values())
        if self._discount_percent > 0:
            discount_amount = subtotal * (self._discount_percent / 100)
            return subtotal - discount_amount
        return subtotal

    def reset(self) -> None:
        """
        Clear all items from the register.

        Resets the register to its initial empty state.
        """
        self._items.clear()
