from actions import commands
from copy import deepcopy
from file_utils import *
from path_utils import *
from pprint import pprint
from typing import Any


class DataNavigator:
    """Terminal data navigator"""
    def __init__(self,
                 data: Any,
                 path: str = "",
                 filename: str = "lipsum.json",
                 literal: bool = False) -> None:
        self.secure_data = data
        self.data = deepcopy(self.secure_data)
        self.path = path
        self.filename = filename
        self.literal = literal
        self.commands: dict = commands
    
    @property
    def public_vars(self) -> dict:
        public = {
            "commands": self.commands,
            "data": self.data,
            "filename": self.filename,
            "literal": self.literal,
            "path": self.path
        }
        return public

    def run(self) -> None:
        """Run data navigator REPL ambient"""
        while True:
            pprint(get_data_by_path(self.data, self.path))
            print("\n")

            command, *args = input(f"  >").split(" ")
            
            if command in self.commands:
                self.commands[command](self, args)
            else:
                print("ERROR: Invalid command.")
