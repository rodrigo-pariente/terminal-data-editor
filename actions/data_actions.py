"""Module for storing DataEditor REPL possible actions."""

import argparse
from collections.abc import Callable
import logging
from pathlib import Path
from pprint import pprint
from typing import Any, TYPE_CHECKING

from actions.action_exceptions import ActionError
from parsing.repl_parser import AttemptToExitError, CommandParser
from read_and_write import read_file
from utils.data_utils import smart_cast, iter_data
from widgets.quick_fill import QuickFill


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from widgets.data_editor import DataEditor


data_editor_parser = CommandParser(
    prog="Data Editor", description="A widget to edit data of a file",
    add_help=False, commands_description="Commands to edit ✍️"
)

de_parser = data_editor_parser  # enshortened name for using decorators # start with _?

@de_parser.add_args("+l", "--literal", dest="literal", action="store_true")
@de_parser.add_args(
    "-p", "--path", nargs="?", default=".", type=Path,
    help="path of value append"
)
@de_parser.add_args("new_values", nargs="+")
@de_parser.add_cmd("append", prefix_chars="-+")
def append_data(
    de: "DataEditor",
    new_values: list[str],
    path: Path,
    literal: bool
) -> None:
    """
    Append data.
    """
    for value in new_values:
        try:
            sel_data: Any = de.get_data(path)
        except IndexError as e:
            raise ActionError(e)

        new_data: Any = smart_cast(value)

        match (new_data, sel_data):
            case (dict(), dict()):
                sel_data.update(new_data)

            case (list(), list()):
                sel_data.extend(new_data)

            case _:
                appended: Any
                try:
                    appended = sel_data + new_data
                except TypeError:
                    if not literal:
                        raise ActionError(f"Could not append {new_data}.")
                    appended = "".join(map(str, (sel_data, new_data)))

                de.change_data(appended, path)

@de_parser.add_args(
    "path", nargs="?", default=".", type=Path,
    help="path of data to cast."
)
@de_parser.add_cmd("cast")
def cast_value(de: "DataEditor", path: Path) -> None:
    """Smart cast data in given path."""
    data: Any = de.get_data(path)
    de.change_data(str(data), path, force_type=True)

@de_parser.add_args(
    "path", nargs="?", default=Path("."), type=Path,
    help="path of data to uncast."
)
@de_parser.add_cmd("uncast")
def uncast_value(de: "DataEditor", path: Path) -> None:
    """Cast data in given path as str."""
    data: Any = de.get_data(path)
    de.change_data(str(data), path, force_type=True)

@de_parser.add_args(
    "-r", "--recursively", action="store_true", help="delete recursively."
)
@de_parser.add_args(
    "-p", "--path", nargs="?", default=".", type=Path,
    help="path of value to delete"
)
@de_parser.add_args(metavar="values", nargs="+", dest="keys_to_delete")
@de_parser.add_cmd("del-key")
def del_key(
    de: "DataEditor",
    keys_to_delete: list[str],
    path: Path,
    recursively: bool
) -> None:
    """Delete value, key or item based on given key."""    
    def _iter_del(data, keys_to_delete, recursively):
        if isinstance(data, list):
            return [
                _iter_del(v, keys_to_delete, recursively) if recursively
                else v for i, v in enumerate(data) if i not in keys_to_delete
            ]

        elif isinstance(data, dict):
            return {
                k: _iter_del(v, keys_to_delete, recursively) if recursively
                else v for k, v in data.items() if k not in keys_to_delete
            }

        return data

    data: Any = de.get_data(path)

    keys_to_delete: tuple[Any, ...] = tuple(
        smart_cast(value) if de.literal else value
        for value in keys_to_delete
    )

    new_value: Any = _iter_del(data, keys_to_delete, recursively)
    de.change_data(new_value, path, force_type=True)

@de_parser.add_args(
    "-r", "--recursively", action="store_true", help="delete recursively."
)
@de_parser.add_args(
    "-p", "--path", nargs="?", default=".", type=Path,
    help="path of value to delete"
)
@de_parser.add_args(metavar="values", nargs="+", dest="values_to_delete")
@de_parser.add_cmd("del-val")
def del_val(
    de: "DataEditor",
    values_to_delete: list[str],
    path: Path,
    recursively: bool
) -> None:
    """Delete value, key or item based on given value."""    
    def _iter_del(data, values_to_delete, recursively):
        if data in values_to_delete:
            return None

        if isinstance(data, list):
            return [
                _iter_del(i, values_to_delete, recursively) if recursively
                else i for i in data if i not in values_to_delete
            ]

        elif isinstance(data, dict):
            return {
                k: _iter_del(v, values_to_delete, recursively) if recursively
                else v for k, v in data.items() if v not in values_to_delete
            }

        return data

    data: Any = de.get_data(path)

    values_to_delete: tuple[Any, ...] = tuple(
        smart_cast(value) if de.literal else value
        for value in values_to_delete
    )

    new_value: Any = _iter_del(data, values_to_delete, recursively)
    de.change_data(new_value, path, force_type=True)

@de_parser.add_args("path", nargs="?", default=Path("."), type=Path)
@de_parser.add_cmd("ls", "list")  
def list_data(de: "DataEditor", path: Path) -> None:
    """Print data in given data path."""
    pprint(de.get_data(path))

@de_parser.add_args("path", nargs="?", default=Path("."), type=Path)
@de_parser.add_cmd("cd")
def change_editor_path(de: "DataEditor", path: Path)-> None:
    """Move path."""
    de.path = de.resolve_path(path)

@de_parser.add_cmd("qf", "quick-fill")
def quick_fill(de: "DataEditor") -> None:
    """Editing mode for quick filling dict values and list items."""
    def _data_answer(data):
        print(f"data: {data}")
        return smart_cast(input("new value: "))
    
    def _list_answer(i, item):
        print(f"i: {i}, item: {item}")
        return smart_cast(input("item: "))

    def _dict_answer(key, value):
        print(f"{key}: {value}")
        return smart_cast(input(f"{key}: "))

    de.data: Any
    de.data = iter_data(de.data, _dict_answer, _list_answer, _data_answer)

@de_parser.add_args("variables", nargs="*")
@de_parser.add_cmd("print")
def print_attr(de: "DataEditor", variables: list[str]) -> None:
    """Show variable value based on it's name."""
    variables: list[str] = variables
    public_attr: dict[str, Any] = {
        "data": de.data,
        "filename": de.filename,
        "literal": de.literal,
        "path": de.path
    }
    if not variables:
        print("Available variables: ", ", ".join(public_attr.keys()))
        return

    for var in variables:
        print(f"{var}: {public_attr.get(var, 'Variable not found')}")

@de_parser.add_cmd("restart")
def restart(de: "DataEditor") -> None:
    """Restart DataEditor data to the original state."""
    if de.filename is not None:
        de.data: Any = read_file(de.filename)
    else:
        print("ERROR: No file is opened.")

@de_parser.add_args("mode", choices=["on", "off"])
@de_parser.add_cmd("literal")
def set_literal(de: "DataEditor", literal: bool, mode: str) -> None:
    """Set DataEditor flag on or off."""
    de.literal: bool = bool(mode == "on")

@de_parser.add_args("+l", "--literal", dest="literal", action="store_true")
@de_parser.add_args("-p", "--path", default=Path("."), type=Path)
@de_parser.add_args("new_value", nargs="+")
@de_parser.add_cmd("set", prefix_chars="-+")
def set_value(
    de: "DataEditor",
    new_value: list[str],
    path: Path,
    literal: bool
) -> None:
    """Set new value."""
    new_value: Any
    new_value = " ".join(new_value)
    if literal:
        new_value = smart_cast(" ".join(new_value))

    de.change_data(new_value, path, force_type=literal)
