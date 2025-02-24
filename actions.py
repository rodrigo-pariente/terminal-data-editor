from collections.abc import Callable
from data_utils import *
from file_utils import *
import os
from pprint import pprint
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data_navigator import DataNavigator

commands = {}

def add_command(command: str) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(func):
        commands[command] = func
        return func
    return wrapper

@add_command("append") # has a problem on appending data passed with spaces char
def append_data(dn: "DataNavigator", args):
    """Append data in current path without rewriting all data to maintain."""
    masked_data = get_data_by_path(dn.data, dn.path)
    
    for arg in args:
        current = smart_cast(arg)
        to_compare = [current, masked_data]
        if all(isinstance(d, dict) for d in to_compare):
            masked_data.update(current)
        
        elif all(isinstance(d, list) for d in to_compare):
            masked_data.extend(current)
        
        elif all(isinstance(d, (int, float, str)) for d in to_compare):
            masked_data = {masked_data} + {current}
        
        else:
            print(f"Could not append {current}.")

@add_command("quit")
@add_command("exit")
def exit(*args) -> None:
    """Exit the script."""
    sys.exit(0)

@add_command("flag")
def flag(dn: "DataNavigator", args) -> None:
    if len(args) == 2 and isinstance(smart_cast(args[1]), bool):
        flag = args[0]
        value = smart_cast(args[1])
        dn.set_flag(flag, value)
    else: 
        print("usage: flag <flag> [bool value]")

@add_command("cd")
def move(dn: "DataNavigator", indexes: list[str] | str) -> None:
    """Move path based on given indexes."""
    pprint(get_data_by_path(dn.data, dn.path))
    if isinstance(indexes, str):
        p = Path(indexes)
    else:
        p = Path("")
        for i in range(len(indexes)):
            p = p.joinpath(indexes[i])

    for i in p.parts:
        masked_data = get_data_by_path(dn.data, dn.path)

        if i == "..":
            if dn.path:
                dn.path = dn.path.parent
            else:
                print("ERROR: You are at root level.")

        elif isinstance(masked_data, dict):
            if i in masked_data:
                dn.path = dn.path.joinpath(i)
            else:
                print("ERROR: Key not found in dictionary.")
        
        elif isinstance(masked_data, list):
            if i.isdigit() and 0 <= int(i) < len(masked_data):
                dn.path = dn.path.joinpath(i)
            else:
                print("ERROR: Invalid list index.")

        else:
            print("ERROR: Cannot navigate into this type.")

@add_command("ls")
@add_command("list")
def list_data(dn: "DataNavigator", *args):
    pprint(get_data_by_path(dn.data, dn.path))

@add_command("restart")
def restart(dn: "DataNavigator", *args) -> None:
    """Restart DataNavigator data to the original state."""
    pprint(get_data_by_path(dn.data, dn.path))
    dn.data = read_file(dn.filename)

@add_command("save")
def save(dn: "DataNavigator", *args) -> None:
    """Save DataNavigator modified data into filename."""
    save_json(dn.filename, dn.data)
    print(f"Saved at {dn.filename}.")

@add_command("set")
def set(dn: "DataNavigator", new_values: list[str]) -> None:
    """Set new value in current path data."""
    pprint(get_data_by_path(dn.data, dn.path))
    for nv in new_values:
        nv = nv if not dn.literal else smart_cast(nv)
        dn.data = change_data_by_path(dn.data, dn.path, nv)

@add_command("print")
def print_public(dn: "DataNavigator", var_name: list[str]) -> None:
    """Show variable value based on it's name."""
    for var in var_name:
        if var in dn.public:
            print(f"{var}: {dn.public[var]}")
        else:
            print(f"Couldn't find variable {var}")

@add_command("!")
def run_command(_, args) -> None:
    """Let you pass shell commands without leaving the application."""
    os.system(*args)

