"""Common actions between navigators."""

from collections.abc import Callable
import os
from pathlib import Path
import sys
from typing import Any, TYPE_CHECKING
from read_and_write import read_file


if TYPE_CHECKING:
    from navigators import NavigatorManager

common_commands: dict[str, Callable] = {}

def add_command(*commands_list: tuple[str, ...]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(action):
        for command in commands_list:
            common_commands[command] = action
    return wrapper

@add_command("cls", "clear")
def clear_screen(*_) -> None:
    """Clean the screen without leaving the REPL"""
    os.system("cls" if os.name == "nt" else "clear")

@add_command("edit")
def edit_file(nm: "NavigatorManager", file: list[str]) -> None:
    """Open file in DataNavigator instance"""
    filename: str = " ".join(file)
    abs_filename: Path = (nm.file_navigator.path / filename).resolve()

    data: Any = read_file(abs_filename)
    nm.data_navigator.path = Path()
    nm.data_navigator.filename = abs_filename
    nm.data_navigator.data = data

    nm.active_navigator = nm.data_navigator

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
