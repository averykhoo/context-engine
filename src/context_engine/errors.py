"""Refusals: every one says what is wrong and what to do about it (FRAMEWORK §8.0, P7)."""


class Refusal(Exception):
    """A write or a check the engine will not carry out. ``remedy`` is never empty."""

    def __init__(self, message: str, remedy: str):
        if not remedy:
            raise ValueError("a Refusal must name its remedy")
        super().__init__(f"refused: {message}. Remedy: {remedy}")
        self.message = message
        self.remedy = remedy
