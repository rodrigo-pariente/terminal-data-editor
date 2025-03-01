"""Module for navigator repl widgets."""

import dataclasses
from pathlib import Path
from typing import Any
from common_actions import common_commands
from data_actions import data_commands
from data_utils import change_data_by_path, get_data_by_path, smart_cast
from file_actions import file_commands


class DataNavigator:
    """Terminal data navigator"""
    def __init__(self,
                 data: Any,
                 filename: str,
                 path: Path = Path(),
                 literal: bool = True) -> None:
        self.data = data
        self.path = path
        self.filename = filename
        self.literal = literal
        self.commands: dict = data_commands

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

@dataclasses.dataclass
class FileNavigator:
    """Terminal file navigator"""
    path: Path = Path(Path.cwd().anchor)
    commands: dict = dataclasses.field(
        default_factory=lambda: file_commands.copy()
    )

def compositor(
        data_navigator: DataNavigator,
        file_navigator: FileNavigator) -> None:
    """
    Function for organizing navigator widgets.
    Also contain a pre-repl for higher commands.
    """
    active_navigator = file_navigator
    while True:
        command, *args = input(">>>").strip().split()

        match command.lower():
            case _ if command in active_navigator.commands:
                active_navigator.commands[command](active_navigator, args)
            case _ if command in common_commands:
                common_commands[command](args)
            case "explorer":
                active_navigator = file_navigator
            case "editor":
                active_navigator = data_navigator
            case _:
                print("ERROR: Invalid command.")
