"""Module for holding QuickFill, widget for fast filling data."""

from typing import Any

from utils.data_utils import smart_cast, iter_data


class QuickFill:
    """QuickFill class widget for quick filling data"""
    def __init__(self, data: Any) -> None:
        self.data = data

    def run(self) -> None:
        """Run widget REPL"""
        def data_answer(data):
            print(f"data: {data}")
            return smart_cast(input("new value: "))
        
        def list_answer(i, item):
            print(f"i: {i}, item: {item}")
            return smart_cast(input("item: "))

        def dict_answer(key, value):
            print(f"{key}: {value}")
            return smart_cast(input(f"{key}: "))

        iter_data(self.data, dict_answer, list_answer, data_answer)
