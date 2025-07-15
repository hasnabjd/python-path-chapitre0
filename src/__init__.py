"""
Source package for the cash register application.

This package contains the main modules for the cash register functionality.
"""

from .register import CashRegister
from .exceptions import NegativePriceError

__version__ = "1.0.0"

__all__ = [
    "CashRegister",
    "NegativePriceError",
]
