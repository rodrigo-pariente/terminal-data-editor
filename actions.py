"""Module for storing DataNavigator REPL possible actions."""

from collections.abc import Callable
import os
from pathlib import Path
from pprint import pprint
import sys
from typing import TYPE_CHECKING
from data_utils import smart_cast, change_data_by_path
from file_utils import read_file, save_file


if TYPE_CHECKING:
    from data_navigator import DataNavigator

commands = {}

def add_command(*commands_list: list[str]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(func):
        for command in commands_list:
            commands[command] = func
        return func
    return wrapper

@add_command("append")
def append_data(dn: "DataNavigator", args) -> None:
    """Append data in current path without rewriting all data to maintain."""
    new_data = smart_cast(" ".join(args))

    to_compare = (new_data, dn.dn.cur_data)
    if all(isinstance(d, dict) for d in to_compare):
        dn.cur_data.update(new_data)

    elif all(isinstance(d, list) for d in to_compare):
        dn.cur_data.extend(new_data)

    elif all(isinstance(d, (int, float, str)) for d in to_compare):
        if isinstance(dn.cur_data, str) or isinstance(new_data, str):   
            dn.cur_data = str(dn.cur_data)
            new_data = str(new_data)
        set(dn, [f"{dn.cur_data + new_data}"])

    else:
        print(f"Could not append {new_data}.")

@add_command("cast")
def cast_value(dn: "DataNavigator", args: list[str]) -> None:
    """Smart cast data in given path."""
    if len(args) == 1:
        tmp = dn.path
        if args[0] != ".":
            dn.path = Path(args[0])

        set(dn, [smart_cast(dn.cur_data)])

        dn.path = tmp
    else:
        print("usage: cast <path>")

@add_command("cls", "clear")
def clear_screen(*_) -> None:
    """Clean the screen without leaving the REPL"""
    os.system("cls" if os.name == "nt" else "clear")

@add_command("del-key")
def del_key(dn: "data_navigator", indexes: list[str]) -> None:
    """Delete data based on given index."""
    for i in indexes:
        if isinstance(dn.cur_data, (dict, list)):
            try:
                dn.cur_data.pop(i)
            except (KeyError, IndexError):
                print("No value of index {i} in data.")
        else:
            print("Can only del-key from dictionary or list only.")

@add_command("del-val")
def del_val(dn: "DataNavigator", values: list[str]) -> None:
    """Delete value, key or item based on given value."""

    for i in values:
        if i == ".":
            set(dn, ["None"], show=False)
            cast_value(dn, ["."]) # make sure deleted value now is NoneType

        elif isinstance(dn.cur_data, dict):
            dn.cur_data = {k: v for k, v in dn.cur_data.items() if v != i}

        elif isinstance(dn.cur_data, list):
            dn.cur_data.remove(i)

        else:
            print(f"Could not delete {i}.")

@add_command("exit", "quit")
def exit_repl(*_) -> None:
    """Exit the script."""
    sys.exit(0)

@add_command("flag")
def flag_set(dn: "DataNavigator", args) -> None:
    """Set dn attr True or False if attr is boolean."""
    if len(args) == 2 and args[1].lower() in ("on", "off"):
        flag = args[0]
        value = bool(args[1].lower() == "on")
        dn.set_flag(flag, value)
    else:
        print("usage: flag <flag> [bool value]")

@add_command("cd")
def move(dn: "DataNavigator", indexes: list[str] | str) -> None:
    """Move path based on given indexes."""
    if isinstance(indexes, str):
        p = Path(indexes)
    else:
        p = Path("")
        for i in indexes:
            p = p.joinpath(i)

    for i in p.parts:
        if i == "..":
            if dn.path.as_posix() != ".":
                dn.path = dn.path.parent
            else:
                print("ERROR: You are at root level.")

        elif isinstance(dn.cur_data, dict):
            if i in dn.cur_data:
                dn.path = dn.path.joinpath(i)
            else:
                print("ERROR: Key not found in dictionary.")

        elif isinstance(dn.cur_data, list):
            if i.isdigit() and 0 <= int(i) < len(dn.cur_data):
                dn.path = dn.path.joinpath(i)
            else:
                print("ERROR: Invalid list index.")

        else:
            print("ERROR: Cannot navigate into this type.")

    pprint(dn.cur_data)

@add_command("ls", "list")
def list_data(dn: "DataNavigator", *_) -> None:
    """Print data in current working data path."""
    pprint(dn.cur_data)

@add_command("print")
def print_public(dn: "DataNavigator", var_name: list[str]) -> None:
    """Show variable value based on it's name."""
    for var in var_name:
        if var in dn.public:
            print(f"{var}: {dn.public[var]}")
        else:
            print(f"Couldn't find variable {var}")

@add_command("restart")
def restart(dn: "DataNavigator", *_) -> None:
    """Restart DataNavigator data to the original state."""
    dn.data = read_file(dn.filename)
    pprint(dn.cur_data)

@add_command("!")
def run_command(_, args) -> None:
    """Let you pass shell commands without leaving the application."""
    string_command = " ".join(args)
    os.system(string_command)

@add_command("save")
def save(dn: "DataNavigator", *_) -> None:
    """Save DataNavigator modified data into filename."""
    save_file(dn.filename, dn.data)
    print(f"Saved at {dn.filename}.")

@add_command("set")
def set_value(dn: "DataNavigator", new_values: list[str], show: bool = False) -> None:
    """Set new value in current path data."""
    for nv in new_values:
        nv = nv if not dn.literal else smart_cast(nv)
        dn.data = change_data_by_path(dn.data, dn.path, nv)
    if show:
        pprint(dn.cur_data)
