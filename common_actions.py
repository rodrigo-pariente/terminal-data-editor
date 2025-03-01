"""Common actions between navigators."""
from collections.abc import Callable
import os
import sys

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

@add_command("exit", "quit", "q")
def exit_repl(*_) -> None:
    """Exits the application."""
    sys.exit(0)

@add_command("!")
def shell_commands(args: list[str]) -> None:
    """Let user pass shell commands without leaving the application."""
    if not args:
        print("Usage: ! <shell command>")
        return
    os.system(" ".join(args))
