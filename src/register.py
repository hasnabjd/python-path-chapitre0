from decimal import Decimal
from typing import Dict
from .exceptions import NegativePriceError


class CashRegister:
    """
    A simple cash register to scan items, calculate the total, and reset.

    Attributes:
        _items (Dict[str, Decimal]): Internal dictionary to track item totals by SKU.
    """

    def __init__(self):
        """Initialize an empty cash register."""
        self._items: Dict[str, Decimal] = {}

    def scan_item(self, sku: str, price: Decimal, qty: int = 1):
        """
        Add one or more units of an item to the register.

        Args:
            sku (str): The stock-keeping unit (product code).
            price (Decimal): Price of a single unit.
            qty (int): Number of units to add (default is 1).

        Raises:
            NegativePriceError: If the price is zero or negative.

        Side effects:
            Updates the internal total for the given SKU.
        """
        if price <= 0:
            raise NegativePriceError(price)
        
        total_price = price * qty
        self._items[sku] = self._items.get(sku, Decimal("0.00")) + total_price

    def total(self) -> Decimal:
        """
        Compute the total amount for all scanned items.

        Returns:
            Decimal: The total cost of all items scanned so far.
        """
        return sum(self._items.values())

    def reset(self) -> None:
        """
        Clear all items from the register.

        Resets the register to its initial empty state.
        """
        self._items.clear()
