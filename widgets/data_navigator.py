"""Module for navigator repl widgets."""

from pathlib import Path
from typing import Any
from actions.data_actions import data_commands
from utils.data_utils import change_data_by_path, get_data_by_path, smart_cast


class DataNavigator:
    """Terminal data navigator"""
    def __init__(self,
                 data: Any = None,
                 filename: str | None = None,
                 path: Path = Path(),
                 literal: bool = True) -> None:
        self.data = data
        self.path = path
        self.filename = filename
        self.literal = literal
        self.commands: dict = data_commands.copy()

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
