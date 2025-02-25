"""
Module for setting class DataNavigator for
creating a REPL ambient as an object.
"""

from pathlib import Path
from pprint import pprint
from typing import Any
from actions import commands
from data_utils import change_data_by_path, get_data_by_path, smart_cast

class DataNavigator:
    """Terminal data navigator"""
    def __init__(self,
                 data: Any,
                 path: Path = "",
                 filename: str = "lipsum.json",
                 literal: bool = False) -> None:
        self.data = data
        self.path = path
        self.filename = filename
        self.literal = literal
        self.commands: dict = commands

    @property
    def cur_data(self) -> Any:
        """Return current data as given working path."""
        return get_data_by_path(self.data, self.path)

    @cur_data.setter
    def cur_data(self, value: Any) -> None:
        """Setter for easy changes in data of current working path"""
        value = smart_cast(value) if self.literal else value
        self.data = change_data_by_path(self.data, self.path, value)

    @property
    def public(self) -> dict:
        """Public variables that can be acessed externally."""
        public = {
            "data": self.data,
            "filename": self.filename,
            "literal": self.literal,
            "path": self.path
        }
        return public

    def flag_setter(self, flag: str, value: bool) -> None:
        """Set boolean public attributes."""
        if flag in self.public and isinstance(self.public[flag], bool):
            setattr(self, flag, value)
        else:
            print("Coulself't find flag.")

    def run(self) -> None:
        """Run data navigator REPL ambient"""
        pprint(get_data_by_path(self.data, self.path))
        while True:
            command, *args = input(">>>").split(" ")

            if command in self.commands:
                self.commands[command](self, args)
            else:
                print("ERROR: Invalid command.")
