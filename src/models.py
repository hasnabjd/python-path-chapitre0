from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class LineItem:
    """
    Represents a single line item in a receipt.
    
    Attributes:
        sku (str): Stock-keeping unit (product code)
        qty (int): Quantity of items
        unit_price (Decimal): Price per unit
    """
    sku: str
    qty: int
    unit_price: Decimal
    
    @property
    def total_price(self) -> Decimal:
        """Calculate the total price for this line item."""
        return self.unit_price * self.qty


@dataclass
class Receipt:
    """
    Represents a complete receipt with all line items and totals.
    
    Attributes:
        lines (List[LineItem]): List of all line items
        total_gross (Decimal): Subtotal before discount (total brut)
        discount_pct (Decimal): Discount percentage applied
        total_due (Decimal): Final total after discount
    """
    lines: List[LineItem]
    total_gross: Decimal
    discount_pct: Decimal
    total_due: Decimal 