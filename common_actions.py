"""Common actions between navigators."""

from collections.abc import Callable
import os
from pathlib import Path
import sys
from typing import Any
from file_utils import read_file


common_commands: dict = {}

def add_command(*commands_list: tuple[str, ...]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(func):
        for command in commands_list:
            common_commands[command] = func
        return func
    return wrapper

@add_command("cls", "clear")
def clear_screen(*_) -> None:
    """Clean the screen without leaving the REPL"""
    os.system("cls" if os.name == "nt" else "clear")

@add_command("edit")
def edit_file(dn: "DataNavigator", fn: "FileNavigator", file: list[str]) -> None:
    """Open file in DataNavigator instance"""
    filename: str = " ".join(file)
    abs_filename: Path = (fn.path / filename).resolve()

    data: Any = read_file(abs_filename)
    dn.path = Path()
    dn.filename = abs_filename
    dn.data = data

@add_command("exit", "quit", "q")
def exit_repl(*_) -> None:
    """Exits the application."""
    sys.exit(0)

@add_command("!")
def shell_commands(_, __, args: list[str]) -> None:
    """Let user pass shell commands without leaving the application."""
    if not args:
        print("Usage: ! <shell command>")
        return
    os.system(" ".join(args))
