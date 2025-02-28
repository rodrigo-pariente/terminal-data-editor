"""
Module for setting class DataNavigator for
creating a REPL ambient as an object.
"""

from pathlib import Path
from pprint import pprint
from typing import Any
from data_actions import commands
from data_utils import change_data_by_path, get_data_by_path, smart_cast

class DataNavigator:
    """Terminal data navigator"""
    def __init__(self,
                 data: Any,
                 path: Path = Path(),
                 filename: str = "lipsum.json",
                 literal: bool = False) -> None:
        self.data = data
        self.path = path
        self.filename = filename
        self.literal = literal
        self.commands: dict = commands

    def get_data(self, path: Path | str = "current") -> Any:
        """Get DataNavigator based on a path, current if none is given."""
        if isinstance(path, str) and path.lower() == "current":
            path = self.path

        return get_data_by_path(self.data, path)

    def change_data(self,
                    new_value: Any,
                    path: Path | str = "current",
                    force_type: bool = False) -> None:
        """
        Change DataNavigator data based on a path, current if none is given.
        Can force value to be or not casted.
        """
        if isinstance(path, str) and path.lower() == "current":
            path = self.path

        if not force_type:
            if self.literal:
                new_value = smart_cast(new_value)
            else:
                new_value = str(new_value)

        self.data = change_data_by_path(self.data, path, new_value)

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
            command, *args = input(">>>").strip().split()

            if command in self.commands:
                self.commands[command](self, args)
            else:
                print("ERROR: Invalid command.")
