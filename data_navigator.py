import actions
from utils import *
from json_utils import *
from typing import Any
from copy import deepcopy

class DataNavigator:
    """Terminal data navigator"""
    def __init__(self,
                 data: Any,
                 path: str = "",
                 filename: str = "lipsum.json",
                 literal: bool = False) -> None:
        self.secure_data: Any = data
        self.data: Any = deepcopy(self.secure_data)
        self.path = path
        self.filename: str = filename
        self.literal: bool = literal
        self.commands: dict = actions.actions

    def _move(self, index: str) -> None:
        """Move path based on given index."""
        for i in safe_path_split(index):
            if isinstance(get_data_by_path(self.data, self.path), dict):
                if i in get_data_by_path(self.data, self.path):
                    self.path = path_append(self.path, i)
                else:
                    print("ERROR: Key not found in dictionary.")
            
            elif isinstance(get_data_by_path(self.data, self.path), list):
                if i.isdigit() and 0 <= int(i) < len(get_data_by_path(self.data, self.path)):
                    self.path = path_append(self.path, i)
                else:
                    print("ERROR: Invalid list index.")

            else:
                print("ERROR: Cannot navigate into this type.")

    def run(self) -> None:
        """Run data navigator ambient"""
        while True:
            print(get_data_by_path(self.data, self.path), "\n")

            index = input(f"{self.path}/")
            
            if index in self.commands:
                self.commands[index](self)
            elif index[0] == "\\" and len(index) >= 2:
                new_value = index[1:] if not self.literal else smart_cast(index[1:])
                self.data = change_data_by_path(self.data, self.path, new_value)
            else:
                self._move(index)


if __name__ == "__main__":
    filename = "foo.json"
    data = open_json(filename)
    dn = DataNavigator(data, filename=filename, literal=True)
    dn.run()
