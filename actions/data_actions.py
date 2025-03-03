"""Module for storing DataNavigator REPL possible actions."""

from collections.abc import Callable
from pathlib import Path
from pprint import pprint
from typing import Any, TYPE_CHECKING
from utils.data_utils import smart_cast
from read_and_write import read_file, write_file


if TYPE_CHECKING:
    from widgets.data_navigator import DataNavigator

data_commands: dict[str, Callable]  = {}

def add_command(*commands_list: list[str]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(action: Callable) -> None:
        for command in commands_list:
            data_commands[command]: Callable = action
    return wrapper

@add_command("qf", "quick-fill")
def quick_fill(dn: "DataNavigator", *_) -> None:
    """Editing mode for quick filling dict values and list items."""
    def qf(data: Any) -> Any:
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    qf(item)
                else:
                    print(f"i: {i}, item: {item}")
                    data[i] = smart_cast(input("item: "))

        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    qf(value)
                else:
                    print(f"{key}: {value}")
                    data[key] = smart_cast(input(f"{key}: "))

        else:
            print(f"data: {data}")
            data = smart_cast(input("new value: "))

        return data
    qf(dn.data)

@add_command("append")
def append_data(dn: "DataNavigator", args) -> None:
    """Append data in current path without rewriting all data to maintain."""
    new_data = smart_cast(" ".join(args))
    cur_data = dn.get_data("current")

    match (new_data, cur_data):
        case (dict(), dict()):
            cur_data.update(new_data)

        case (list(), list()):
            cur_data.extend(new_data)

        case (a,b) if all(isinstance(d, (int, str, float)) for d in (a,b)):
            if isinstance(cur_data, str) or isinstance(new_data, str):
                cur_data: str = str(cur_data)
                new_data: str = str(new_data)
            dn.change_data(f"{cur_data + new_data}", "current")

        case _:
            print(f"Could not append {new_data}.")

@add_command("cast")
def cast_value(dn: "DataNavigator", args: list[str]) -> None:
    """Smart cast data in given path."""
    if len(args) != 1:
        print("Usage: cast <path>")
        return
    path: str = "current" if args[0] == "." else args[0]
    data: Any = dn.get_data(path)
    dn.change_data(smart_cast(data), path, force_type=True)

@add_command("del-key")
def del_key(dn: "DataNavigator", indexes: list[str]) -> None:
    """Delete data based on given index."""
    cur_data: Any = dn.get_data("current")
    for i in indexes:
        if isinstance(cur_data, (dict, list)):
            try:
                cur_data.pop(i)
            except (KeyError, IndexError):
                print("No value of index {i} in data.")
        else:
            print("Can only del-key from dictionary or list only.")

@add_command("del-val")
def del_val(dn: "DataNavigator", values: list[str]) -> None:
    """Delete value, key or item based on given value."""
    cur_data: Any = dn.get_data("current")
    for i in values:
        if dn.literal:
            i: Any = smart_cast(i)

        if i == ".":
            new_value: None = None

        if isinstance(cur_data, dict):
            new_value: dict[str, Any] = {}
            new_value |= {k: v for k, v in cur_data.items() if v != i}
        elif isinstance(cur_data, list):
            new_value: list[Any] = cur_data.remove(i)
        else:
            print(f"Could not delete {i}.")
            continue

        dn.change_data(new_value, "current", force_type=True)

@add_command("cd")
def move(dn: "DataNavigator", indexes: list[str] | str) -> None:
    """Move path based on given indexes."""
    def is_index(index: str, data: dict | list) -> bool:
        if isinstance(data, dict):
            return index in data
        if isinstance(data, list):
            return index.isdigit() and int(index) in range(len(data))
        return False

    for i in Path(*indexes).parts: # maybe its interior be another func
        if i == "..":
            if dn.path.as_posix() != ".":
                dn.path = dn.path.parent
            else:
                print("ERROR: You are at root level.")
        elif i == "\\":
            dn.path = Path(".")
        elif is_index(i, dn.get_data("current")):
            dn.path = dn.path.joinpath(i)
        else:
            print("ERROR: Cannot navigate into this type.")

    pprint(dn.get_data("current"))

@add_command("ls", "list")
def list_data(dn: "DataNavigator", *_) -> None:
    """Print data in current working data path."""
    pprint(dn.get_data("current"))

@add_command("print")
def print_attr(dn: "DataNavigator", var_names: list[str]) -> None:
    """Show variable value based on it's name."""
    public_attr: dict[str, Any] = {
        "data": dn.data,
        "filename": dn.filename,
        "literal": dn.literal,
        "path": dn.path
    }
    if not var_names:
        print("Available variables: ", ", ".join(public_attr.keys()))
        return

    for var in var_names:
        print(f"{var}: {public_attr.get(var, 'Variable not found')}")

@add_command("restart")
def restart(dn: "DataNavigator", *_) -> None:
    """Restart DataNavigator data to the original state."""
    if dn.filename is not None:
        dn.data: Any = read_file(dn.filename)
    else:
        print("ERROR: No file is opened.")
    pprint(dn.get_data("current"))

@add_command("save")
def save(dn: "DataNavigator", *_) -> None:
    """Save DataNavigator modified data into filename."""
    if dn.filename is not None:
        write_file(dn.filename, dn.data)
        print(f"Saved at {dn.filename}.")
    else:
        print("ERROR: No file is opened.")

@add_command("literal")
def set_flag(dn: "DataNavigator", args: list[str]) -> None:
    """Set DataNavigator flag True or False."""
    one_arg: bool = len(args) == 1
    arg_is_str: bool = isinstance(args[0], str)
    value_is_valid: bool = args[0].lower() in ("on", "off")

    if one_arg and arg_is_str and value_is_valid:
        dn.literal: bool = bool(args[0].lower() == "on")
    else:
        print("usage: literal on / literal off")

@add_command("set")
def set_value(dn: "DataNavigator", new_value: list[str], show: bool = True) -> None:
    """Set new value in current path data."""
    dn.change_data(" ".join(new_value), "current")

    if show:
        pprint(dn.get_data("current"))

@add_command("+l")
def temporary_literal(dn: "DataNavigator", args: list[str]) -> None:
    """Quick execution of command with literal on."""
    if args:
        func: str = args[0]
        if func in data_commands:
            tmp_literal: bool = dn.literal
            try:
                set_flag(dn, ["literal", "on"])
                data_commands[func](dn, args[1:])
            finally:
                dn.literal = tmp_literal
            return

    print("Usage: +l <command> [args]")

@add_command("uncast")
def uncast_value(dn: "DataNavigator", args: list[str]) -> None:
    """Cast data in given path as str."""
    if len(args) != 1:
        print("Usage: uncast <path>")
        return
    path: str = "current" if args[0] == "." else args[0]
    data: Any = dn.get_data(path)
    dn.change_data(str(data), path, force_type=True)
