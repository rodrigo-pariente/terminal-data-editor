from actions import commands
from file_utils import *
from data_utils import *
from pathlib import Path
from pprint import pprint
from typing import Any


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
    def cur_data(self):
        """Return current data as given working path."""
        return get_data_by_path(self.data, self.path) 

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

    def set_flag(self, flag: str, value: bool) -> None:
        """Set boolean public attributes."""
        if flag in self.public and isinstance(self.public[flag], bool):
            setattr(self, flag, value)
        else:
            print("Coulself't find flag.")

    def run(self) -> None:
        """Run data navigator REPL ambient"""
        pprint(get_data_by_path(self.data, self.path))
        while True:
            command, *args = input(f">>>").split(" ")
            
            if command in self.commands:
                self.commands[command](self, args)
            else:
                print("ERROR: Invalid command.")
