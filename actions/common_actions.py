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
    nm.active_widget: DataNavigator = nm.data_navigators[-1]

@add_command("close")
def close_widget(nm: "NavigatorManager", args: list[str]) -> None:
    """Close tab of given index or current tabe if no index given."""
    if not args:
        if nm.active_widget is None:
            print("ERROR: No widget is opened.")
            return

        if isinstance(nm.active_widget, DataNavigator):
            nm.data_navigators.remove(nm.active_widget)
        elif isinstance(nm.active_widget, FileNavigator):
            nm.file_navigators.remove(nm.active_widget)
        else:
            raise NotImplementedError("Was passed not implemented widget.")

    else:
        if len(args) != 2 or not args[1].isdigit():
            print("Usage: close <explorer/editor> [tab_index]")
            return

        widget: str = args[0]
        index: int = int(args[1])
        try:
            match widget.lower():
                case "editor" | "d":
                    nm.data_navigators.pop(index)
                case "explorer" | "x":
                    nm.file_navigators.pop(index)
                case _:
                    print("Usage: close <explorer/editor> [tab_index]")
                    return
        except IndexError:
            print("ERROR: Index out of range.")
            return

    nm.automatic_refocus()

@add_command("explorer")
def focus_file_navigator(nm: "NavigatorManager", *_) -> None:
    """Focus NavigatorManager in its FileNavigator instance."""
    if not nm.file_navigators:
        fn: FileNavigator = FileNavigator()
        nm.file_navigators.append(fn)
    nm.active_widget = nm.file_navigators[-1]

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
    nm.active_widget = nm.data_navigators[index]

@add_command("print-tabs", "tabs")
def print_widgets(nm: "NavigatorManager", *_) -> None:
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
