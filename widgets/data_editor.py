"""Module for navigator repl widgets."""

from pathlib import Path
from typing import Any

from actions.data_actions import data_editor_parser
from actions.action_exceptions import ActionError
from utils.data_utils import (
    change_data_by_path, get_data_by_path, smart_cast
)
from parsing.repl_parser import CommandParser


class DataEditor:
    """Terminal data navigator"""
    def __init__(
        self,
        data: Any = None,
        filename: str | None = None,
        path: Path = Path(),
        literal: bool = True
    ) -> None:
        self.data = data
        self.path = path
        self.filename = filename
        self.literal = literal
        self.parser: CommandParser = data_editor_parser

    def get_data(self, path: Path = Path(".")) -> Any:
        """
        Get data from DataEditor at given path.
        If path is "current", then data at current path is returned.
        """
        resolved_path: Path = self.resolve_path(path)
        return get_data_by_path(self.data, resolved_path)

    def change_data(
        self,
        new_value: Any,
        path: Path = Path(),
        force_type: bool = False
    ) -> None:
        """
        Change data using a path.
        force_type: If true, skip new_value handling.
        """
        resolved_path: Path = self.resolve_path(path)

        if not force_type:
            if self.literal:
                new_value = smart_cast(new_value)
            else:
                new_value = str(new_value)

        self.data: Any
        self.data = change_data_by_path(self.data, resolved_path, new_value)

    def resolve_path(self, new_path: Path) -> Path:
        """
        Return absolute path of relative_path.
        Path.resolve() equivalent.
        """
        # Void paths means: get-current-path (de.path)
        if new_path == Path(".") or new_path == self.path:
            return self.path

        # Path("/") means a root path, in data_paths, root path is a void path
        if new_path == Path("/"):
            return Path(".")

        potential_path: Path = self.path / new_path

        # using ".." shows that the path is relative to something
        potential_indexes: list[str] = potential_path.parts
        if ".." in potential_indexes:
            potential_path = Path()
            for index in potential_indexes:
                if index == "..":
                    potential_path = potential_path.parent
                else:
                    potential_path /= index

        # get_data_by_path raises IndexError when a invalid index is given
        try:
            get_data_by_path(self.data, potential_path)
            return potential_path
        except IndexError:
            try:
                get_data_by_path(self.data, new_path)
                return new_path
            except IndexError:
                raise ActionError(f"Invalid path: {new_path}")
