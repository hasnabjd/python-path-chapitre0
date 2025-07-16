"""
Source package for the cash register application.

This package contains the main modules for the cash register functionality.
"""

from .exceptions import NegativePriceError
from .register import CashRegister

__version__ = "1.0.0"

__all__ = [
    "CashRegister",
    "NegativePriceError",
]
