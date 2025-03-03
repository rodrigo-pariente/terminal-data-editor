"""Module for holding QuickFill, widget for fast filling data."""

from typing import Any
from utils.data_utils import smart_cast


class QuickFill:
    """QuickFill class widget for quick filling data"""
    def __init__(self, data: Any) -> None:
        self.data = data

    def _quick_fill(self, data: Any) -> None:
        """Editing mode for quick filling dict values and list items."""
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._quick_fill(item)
                else:
                    print(f"i: {i}, item: {item}")
                    data[i] = smart_cast(input("item: "))

        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._quick_fill(value)
                else:
                    print(f"{key}: {value}")
                    data[key] = smart_cast(input(f"{key}: "))

        else:
            print(f"data: {data}")
            data = smart_cast(input("new value: "))

        return data

    def run(self) -> None:
        """Run widget REPL"""
        self._quick_fill(self.data)
