"""FileNavigator REPL actions"""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING
from shell_utils import copy_anything, delete_anything, move_anything, create_file, create_directory
from messages import perror


if TYPE_CHECKING:
    from file_navigator import FileNavigator

file_commands = {}

def add_command(*commands_list: tuple[str, ...]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(func):
        for command in commands_list:
            file_commands[command] = func
        return func
    return wrapper

def pathify(main_path: Path, possible_relatives: list[str]) -> tuple[Path, ...]:
    """Unify paths with a master path if they're relatives."""
    return tuple((main_path / path).resolve() for path in possible_relatives)

@add_command("cp", "copy")
def copy_files(fn: "FileNavigator", files: list[str]) -> None: # add filters
    """Copy file from source into given destinations."""
    if len(files) < 2:
        print("Usage: copy <source> <destination_1> ...")
        return

    paths: tuple[Path, ...] = pathify(fn.path, files)
    source, *destinations = paths

    for destination in destinations:
        copy_anything(source, destination)

@add_command("mkdir")
def create_directories(fn: "FileNavigator", paths: list[str]) -> None:
    """Create void directories in current directory. Usage mkdir <dir> ..."""
    if not paths:
        print("Usage: mkdir <dirname_1> ...")
        return

    directories: tuple[Path, ...] = pathify(fn.path, paths)
    for directory in directories:
        create_directory(directory)

@add_command("del", "rm")
def delete_files(fn: "FileNavigator", paths: list[str]) -> None:
    """Delete file or folder from current or given directory."""
    if not paths:
        print("Usage: delete <file> ...")
        return

    files: tuple[Path, ...] = pathify(fn.path, paths)
    for file in files:
        delete_anything(file)

@add_command("ls", "list")
def list_files(fn: "FileNavigator", targets: list[str]) -> None:
    """List directory files."""
    if not targets:
        targets = ["."]

    files: list[str] = [t if t != "." else f"{fn.path}"for t in targets]

    paths: tuple[Path, ...] = pathify(fn.path, files)
    for path in paths:
        if path.is_dir():
            for item in path.iterdir():
                print(item)
        elif path.is_file():
            print(path.name)
        else:
            perror("DirectoryOrFileNotFound", filename=path)

@add_command("mk", "make")
def make_files(fn: "FileNavigator", paths: list[str]) -> None:
    """Create blank files in given directory."""
    if not paths:
        print("Usage: make <filename_1> ...")
        return

    files: tuple[Path, ...] = pathify(fn.path, paths)
    for file in files:
        create_file(file)

@add_command("mv", "move")
def move_file(fn: "FileNavigator", paths: list[str]) -> None:
    """
    Move file from source to first destination.
    If more destinations passed, moved file now is COPIED to those places
    """
    if len(paths) < 2:
        print("Usage: move <source> <destination_1> ...")
        return

    files: tuple[Path, ...] = pathify(fn.path, paths)
    source, *destinations = files

    new_path = move_anything(source, destinations[0])

    if len(destinations) > 1:
        for destination in destinations[1:]:
            copy_anything(new_path, destination)

@add_command("cd")
def change_dir(fn: "FileNavigator", args: list[str]) -> None:
    """Move from the current directory.""" 
    new_path = " ".join(args)

    if new_path == "..":
        fn.path = fn.path.parent
        return

    potential_path = (fn.path / new_path).resolve()
    if potential_path.is_dir():
        fn.path = potential_path
    else:
        perror("DirectoryNotFound", dirname=potential_path)

@add_command("command", "commands")
def print_commands(fn: "FileNavigator") -> None:
    """Show available commands""" 
    for command in fn.commands.keys():
        print(command) # make it prettier

@add_command("pwd")
def show_current_directory(fn: "FileNavigator", *_) -> None:
    """Shows current working directory."""
    print(f"PATH: {fn.path}")
