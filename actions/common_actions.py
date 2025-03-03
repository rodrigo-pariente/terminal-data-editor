"""Common actions between navigators."""

from collections.abc import Callable
import os
from pathlib import Path
import sys
from typing import Any, TYPE_CHECKING
from read_and_write import read_file
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator


if TYPE_CHECKING:
    from widgets.navigator_manager import NavigatorManager

common_commands: dict[str, Callable] = {}

def add_command(*commands_list: tuple[str, ...]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(action):
        for command in commands_list:
            common_commands[command] = action
    return wrapper

# widget related
@add_command("edit")
def edit_file(nm: "NavigatorManager", file: list[str]) -> None:
    """Open file in DataNavigator instance"""
    if file:
        filename: str = " ".join(file)
        abs_filename: Path = (nm.file_navigator.path / filename).resolve()
        data: Any = read_file(abs_filename)
        dn: DataNavigator = DataNavigator(data, abs_filename)
    else:
        dn: DataNavigator = DataNavigator()

    nm.data_navigators.append(dn)
    nm.active_navigator: DataNavigator = nm.data_navigators[-1]

@add_command("close")
def close_data_navigator(nm: "NavigatorManager", args: list[str]) -> None:
    """Close editor of given index or current editor active if no index given."""
    if args:
        if len(args) > 1 or not args[0].isdigit():
            print("Usage: close [index]")
            return

        index: int = int(args[0])
        nm.data_navigators.pop(index)
    else:
        if not isinstance(nm.active_navigator, DataNavigator):
            print("ERROR: Select editor to close first.")
            return
        if not nm.data_navigators:
            print("ERROR: No editor opened.")
            return

        nm.data_navigators.remove(nm.active_navigator)

    if nm.data_navigators:
        nm.active_navigator: DataNavigator = nm.data_navigators[-1]
    else:
        nm.active_navigator: FileNavigator = nm.file_navigator

@add_command("explorer")
def focus_file_navigator(nm: "NavigatorManager", *_) -> None:
    """Focus NavigatorManager in its FileNavigator instance."""
    nm.active_navigator = nm.file_navigator

@add_command("editor")
def focus_data_navigator(nm: "NavigatorManager", args: list[str]) -> None:
    """Focus NavigatorManager in its DataNavigator instance."""
    if not nm.data_navigators and not args:
        nm.data_navigators.append(DataNavigator())
        return

    if args:
        if len(args) > 1 or not args[0].isdigit() or not nm.data_navigators:
            print("Usage: editor [index]")
            return
        index: int = int(args[0])
        if index >= len(nm.data_navigators):
            print("ERROR: Not many editors opened.")
            return
    else:
        index: int = 0
    nm.active_navigator = nm.data_navigators[index]

@add_command("ptabs", "pt")
def print_editors(nm: "NavigatorManager", *_) -> None:
    """Print current oppened editors"""
    for i, data_navigator in enumerate(nm.data_navigators):
        print(f"\nindex: {i}\t file: {data_navigator.filename} ")

# unespecific
@add_command("cls", "clear")
def clear_screen(*_) -> None:
    """Clean the screen without leaving the REPL"""
    os.system("cls" if os.name == "nt" else "clear")

@add_command("exit", "quit", "q")
def exit_repl(*_) -> None:
    """Exits the application."""
    sys.exit(0)

@add_command("!")
def shell_commands(_, args: list[str]) -> None:
    """Let user pass shell commands without leaving the application."""
    if not args:
        print("Usage: ! <shell command>")
        return
    os.system(" ".join(args))
