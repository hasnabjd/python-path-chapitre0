from decimal import Decimal


class NegativePriceError(Exception):
    """Raised when a negative or zero price is encountered."""

    def __init__(
        self, price: Decimal, message: str = "Negative price is encountered."
    ) -> None:
        self.price = price
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message} Price: {self.price}"


class DiscountError(Exception):
    """Raised when an invalid discount percentage is provided."""

    def __init__(
        self, percent: Decimal, message: str = "Invalid discount percentage."
    ) -> None:
        self.percent = percent
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message} Percentage: {self.percent}"
