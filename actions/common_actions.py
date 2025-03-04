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
    from widgets.widget_manager import WidgetManager

common_commands: dict[str, Callable] = {}

def add_command(*commands_list: tuple[str, ...]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(action):
        for command in commands_list:
            common_commands[command] = action
    return wrapper

# widget related
@add_command("edit")
def edit_file(nm: "WidgetManager", file: list[str]) -> None:
    """Open file in DataNavigator instance"""
    if file:
        filename: str = " ".join(file)
        abs_filename: Path = (nm.file_navigator.path / filename).resolve()
        data: Any = read_file(abs_filename)
        dn: DataNavigator = DataNavigator(data, abs_filename)
    else:
        dn: DataNavigator = DataNavigator()

    nm.data_navigators.append(dn)
    nm.active_widget: DataNavigator = nm.data_navigators[-1]

@add_command("close")
def close_data_navigator(nm: "WidgetManager", args: list[str]) -> None:
    """Close current or from given index DataNavigator instance."""
    # Close
    if not args and isinstance(nm.active_widget, DataNavigator):
        nm.data_navigators.remove(nm.active_widget)
    elif len(args) == 1 and args[0].isdigit():
        try:
            index: int = int(args[0])
            nm.data_navigators.pop(index)
        except IndexError:
            print("ERROR: Not that many editors opened.")
            return
    else:
        print("Usage: close [tab_index]")
        return

    # Refocus
    if nm.active_widget not in nm.data_navigators:
        if nm.data_navigators:
            nm.active_widget: DataNavigator = nm.data_navigators[-1]
        else:
            nm.active_widget: FileNavigator = nm.file_navigator

@add_command("explorer")
def focus_file_navigator(nm: "WidgetManager", *_) -> None:
    """Focus WidgetManager in its FileNavigator instance."""
    nm.active_widget = nm.file_navigator

@add_command("editor")
def focus_data_navigator(nm: "WidgetManager", args: list[str]) -> None:
    """Focus WidgetManager in its DataNavigator instance."""
    if not args:
        if not nm.data_navigators:
            nm.data_navigators.append(DataNavigator())
        index: int = 0
    elif len(args) == 1 and args[0].isdigit() and nm.data_navigators:
        index: int = int(args[0])
    else:
        print("Usage: editor [index]")
        return

    try:
        nm.active_widget = nm.data_navigators[index]
    except IndexError:
        print("ERROR: Not that many editors opened.")

@add_command("print-tabs", "tabs")
def print_widgets(nm: "WidgetManager", *_) -> None:
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
