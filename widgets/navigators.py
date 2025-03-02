"""Module for navigator repl widgets."""

import dataclasses
from pathlib import Path
from typing import Any
from actions.common_actions import common_commands
from actions.data_actions import data_commands
from actions.file_actions import file_commands
from utils.data_utils import change_data_by_path, get_data_by_path, smart_cast


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
        """Change data using a path. Allows skip new value handling."""
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
    """Terminal file navigator for exploring files."""
    path: Path = Path(Path.cwd().anchor)
    commands: dict = dataclasses.field(
        default_factory=lambda: file_commands.copy()
    )

class NavigatorManager:
    """Object for organizing and integrating navigator widgets."""
    def __init__(self,
                data_navigator: DataNavigator,
                file_navigator: FileNavigator) -> None:
        self.data_navigator = data_navigator
        self.file_navigator = file_navigator
        self.active_navigator = self.file_navigator

    def run(self) -> None:
        """Execute the REPL ambient"""
        while True:
            command, *args = input(">>>").strip().split()

            match command.lower():
                case _ if command in self.active_navigator.commands:
                    self.active_navigator.commands[command](self.active_navigator, args)
                case _ if command in common_commands:
                    common_commands[command](self, args)
                case "explorer" if not args:
                    self.active_navigator = self.file_navigator
                case "editor" if not args:
                    self.active_navigator = self.data_navigator
                case _:
                    print("ERROR: Invalid command.")
