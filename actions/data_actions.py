"""Module for storing DataEditor REPL possible actions."""

import argparse
from collections.abc import Callable
from pathlib import Path
from pprint import pprint
from typing import Any, TYPE_CHECKING

from parsing.repl_parser import (
    AttemptToExitError, CommandParser, parse_and_execute
)
from read_and_write import read_file, write_file
from utils.data_utils import smart_cast
from widgets.quick_fill import QuickFill


if TYPE_CHECKING:
    from widgets.data_editor import DataEditor


data_editor_parser = CommandParser(
    prog="Data Editor", description="A widget to edit data of a file",
    add_help=False, commands_description="Commands to edit ✍️"
)

@data_editor_parser.add_args("new_values", nargs="+")
@data_editor_parser.add_cmd("append")
def append_data(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Append data in current path without rewriting all data to maintain."""
    for value in parsed.new_values:
        new_data = smart_cast(value)
        cur_data = de.get_data("current")

        match (new_data, cur_data):
            case (dict(), dict()):
                cur_data.update(new_data)

            case (list(), list()):
                cur_data.extend(new_data)

            # improve
            case (a,b) if all(isinstance(d, (int, str, float)) for d in (a,b)):
                if isinstance(cur_data, str) or isinstance(new_data, str):
                    cur_data: str = str(cur_data)
                    new_data: str = str(new_data)
                de.change_data(f"{cur_data + new_data}", "current")

            case _:
                print(f"Could not append {new_data}.")

@data_editor_parser.add_args("data_path")
@data_editor_parser.add_cmd("cast")
def cast_value(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Smart cast data in given path."""
    path: str = "current" if parsed.data_path == "." else Path(parsed.data_path)
    data: Any = de.get_data(path)
    de.change_data(smart_cast(data), path, force_type=True)

@data_editor_parser.add_args("indexes", nargs="+")
@data_editor_parser.add_cmd("del-key")  # ⭐ x problem with deleting index of list
def del_key(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Delete data based on given index."""
    indexes: list[str] = parsed.indexes
    cur_data: Any = de.get_data("current")
    for i in indexes:
        if isinstance(cur_data, (dict, list)):
            try:
                cur_data.pop(i)
            except (KeyError, IndexError):
                print("ERROR: No value of index {i} in data.")
        else:
            print("ERROR: Can only del-key from dictionary or list only.")

@data_editor_parser.add_args("values", nargs="+")
@data_editor_parser.add_cmd("del-val")  # deleting only the last (?)
def del_val(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Delete value, key or item based on given value."""    
    values: list[str] = parsed.values
    cur_data: Any = de.get_data("current")
    new_value: Any
    for i in values:
        if de.literal:
            i: Any = smart_cast(i)

        if i == ".":
            new_value = None
        elif isinstance(cur_data, dict):
            new_value: dict[str, Any] = {}
            new_value |= {k: v for k, v in cur_data.items() if v != i}
        elif isinstance(cur_data, list):
            new_value: list[Any] = cur_data.remove(i)
        else:
            print(f"ERROR: Could not delete {i}.")
            continue

        de.change_data(new_value, "current", force_type=True)

@data_editor_parser.add_cmd("ls", "list")  # improve?
def list_data(de: "DataEditor", *_) -> None:
    """Print data in current working data path."""
    pprint(de.get_data("current"))

@data_editor_parser.add_args("indexes", nargs="+")
@data_editor_parser.add_cmd("cd")
def move(de: "DataEditor", parsed: argparse.Namespace)-> None:
    """Move path based on given indexes."""
    def is_index(index: str, data: dict | list) -> bool:
        if isinstance(data, dict):
            return index in data
        if isinstance(data, list):
            return index.isdigit() and int(index) in range(len(data))
        return False

    indexes: list[str] = parsed.indexes
    for i in Path(*indexes).parts: # maybe its interior be another func
        if i == "..":
            if de.path.as_posix() != ".":
                de.path = de.path.parent
            else:
                print("ERROR: You are at root level.")
        elif i == "\\":
            de.path = Path(".")
        elif is_index(i, de.get_data("current")):
            de.path = de.path.joinpath(i)
        else:
            print("ERROR: Cannot navigate into this type.")

    pprint(de.get_data("current"))

@data_editor_parser.add_cmd("qf", "quick-fill")
def quick_fill(de: "DataEditor", *_) -> None:
    """Editing mode for quick filling dict values and list items."""
    QuickFill(de.data).run()

@data_editor_parser.add_args("var_names", nargs="+")
@data_editor_parser.add_cmd("print")
def print_attr(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Show variable value based on it's name."""
    var_names: list[str] = parsed.var_names
    public_attr: dict[str, Any] = {
        "data": de.data,
        "filename": de.filename,
        "literal": de.literal,
        "path": de.path
    }
    if not var_names:
        print("Available variables: ", ", ".join(public_attr.keys()))
        return

    for var in var_names:
        print(f"{var}: {public_attr.get(var, 'Variable not found')}")

@data_editor_parser.add_cmd("restart")
def restart(de: "DataEditor", *_) -> None:
    """Restart DataEditor data to the original state."""
    if de.filename is not None:
        de.data: Any = read_file(de.filename)
    else:
        print("ERROR: No file is opened.")
    pprint(de.get_data("current"))

@data_editor_parser.add_cmd("save")
def save_file(de: "DataEditor", *_) -> None:
    """Save DataEditor modified data into filename."""
    if de.filename is None:
        de.filename: Path = Path(input("filename: "))
    write_file(de.filename, de.data)
    print(f"Saved at {de.filename}.")

@data_editor_parser.add_args("filename", type=str)
@data_editor_parser.add_cmd("saveas")
def save_as(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Change DataEditor file to another and save."""
    new_filename: str = parsed.filename
    if de.filename:
        de.filename = (de.filename.parent / new_filename).resolve()
    else:
        de.filename = (Path.cwd() / new_filename).resolve()
    write_file(de.filename, de.data)
    print(f"Saved at {de.filename}.")

@data_editor_parser.add_args("args", nargs="+")
@data_editor_parser.add_cmd("literal")
def set_literal(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Set DataEditor flag True or False."""
    args = parsed.args
    one_arg: bool = len(args) == 1
    arg_is_str: bool = isinstance(args[0], str)
    value_is_valid: bool = args[0].lower() in ("on", "off")

    if one_arg and arg_is_str and value_is_valid:
        de.literal: bool = bool(args[0].lower() == "on")
    else:
        print("usage: literal on / literal off")

@data_editor_parser.add_args("new_value", nargs="+")
@data_editor_parser.add_cmd("set")
def set_value(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Set new value in current path data."""
    de.change_data(" ".join(parsed.new_value), "current")

@data_editor_parser.add_args("args", nargs="+")
@data_editor_parser.add_args("command", type=str)
@data_editor_parser.add_cmd("+l")
def temporary_literal(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Quick execution of command with literal on."""
    args: list[str] = parsed.args
    command: str = parsed.command
    if command in de.parser.commands.choices:
        tmp_literal: bool = de.literal
        try:
            # set literal on
            parse_and_execute(de, "literal on")
            
            # parse and execute the user command
            try:
                parse_and_execute(de, " ".join([command, *args]))
            except AttemptToExitError:
                return
        finally:
            de.literal = tmp_literal

@data_editor_parser.add_args("data_path", help="path of data to uncast.")
@data_editor_parser.add_cmd("uncast")
def uncast_value(de: "DataEditor", parsed: argparse.Namespace) -> None:
    """Cast data in given path as str."""
    path: str = "current" if parsed.data_path == "." else Path(parsed.data_path)
    data: Any = de.get_data(path)
    de.change_data(str(data), path, force_type=True)
