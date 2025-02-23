from collections.abc import Callable
from path_utils import *
from file_utils import *
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

@add_command("exit")
def exit(*args) -> None:
    """Exit the script."""
    sys.exit(0) # wanted to be break

@add_command("literal_on")
def literal_on(dn: "DataNavigator", *args) -> None:
    """Turn DataNavigator literal flag ON."""
    dn.literal = True

@add_command("literal_off")
def literal_off(dn: "DataNavigator", *args) -> None:
    """Turn DataNavigator literal flag OFF."""
    dn.literal = False

@add_command("cd")
def move(dn: "DataNavigator", indexes: list[str] | str) -> None:
    """Move path based on given indexes."""
    if isinstance(indexes, str):
        handled_indexes: list[str] = safe_path_split(indexes)
    else:
        handled_indexes: list[str] = list()
        for i in indexes:
            handled_indexes.extend(safe_path_split(i))
             
    for i in handled_indexes:
        masked_data = get_data_by_path(dn.data, dn.path)

        if i == "..":
            if dn.path:
                dn.path = path_pop(dn.path)
            else:
                print("ERROR: You are at root level.")

        elif isinstance(masked_data, dict):
            if i in masked_data:
                dn.path = path_append(dn.path, i)
            else:
                print("ERROR: Key not found in dictionary.")
        
        elif isinstance(masked_data, list):
            if i.isdigit() and 0 <= int(i) < len(masked_data):
                dn.path = path_append(dn.path, i)
            else:
                print("ERROR: Invalid list index.")

        else:
            print("ERROR: Cannot navigate into this type.")

@add_command("restart")
def restart(dn: "DataNavigator") -> None:
    """Restart DataNavigator data to the original state."""
    dn.data = dn.secure_data

@add_command("save")
def save(dn: "DataNavigator") -> None:
    """Save DataNavigator modified data into filename."""
    save_json(dn.filename, dn.data)
    print(f"Saved at {dn.filename}.")

@add_command("set")
def set(dn: "DataNavigator", new_values: list[str]) -> None:
    """Set new value in current path data."""
    for nv in new_values:
        nv = nv if not dn.literal else smart_cast(nv)
        dn.data = change_data_by_path(dn.data, dn.path, nv)

@add_command("show")
def print_public_var(dn: "DataNavigator", var_name: list[str]) -> None:
    """Show variable value based on it's name."""
    for var in var_name:
        if var in dn.public_vars:
            print(f"{var}: {dn.public_vars[var]}")
        else:
            print(f"Couldn't find variable {var}")

