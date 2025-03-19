"""
Module for storing Action Error Exception.
They are the safe errors of the execution.
"""

class ActionError(Exception):
    """All ActionErrors are supposed to be catched by the REPLRunner."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
