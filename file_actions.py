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

def pathify(master_path: Path, possible_relatives: list[str]) -> tuple[Path, ...]:
    """Unify paths with a master path if they're relatives."""
    main: Path = master_path
    paths: list[str] = possible_relatives

    paths: tuple[Path, ...] = tuple((main / path).resolve() for path in paths)

    return paths

@add_command("cp", "copy")
def copy_files(fn: "FileNavigator", files: list[str]) -> None: # add filters
    """Copy file from source into given destinations."""
    if len(files) < 2:
        print("Usage: copy <source> <destination_1> ...")
        return

    files: tuple[Path, ...] = [Path(fn.path / file).resolve() for file in files]
    source, *destinations = files

    for destination in destinations:
        copy_anything(source, destination)

@add_command("mkdir")
def create_directories(fn: "FileNavigator", directories: list[str]) -> None:
    """Create void directories in current directory. Usage mkdir <dir> ..."""
    if not directories:
        print("Usage: mkdir <dirname_1> ...")
        return

    directories: tuple[Path, ...] = pathify(fn.path, directories) 
    for directory in directories:
        create_directory(directory)

@add_command("del", "rm")
def delete_files(fn: "FileNavigator", files: list[str]) -> None:
    """Delete file or folder from current or given directory."""
    if not files:
        print("Usage: delete <file> ...")
        return

    files: tuple[Path, ...] = pathify(fn.path, files) 
    for file in files:
        delete_anything(file)

@add_command("ls", "list")
def list_files(fn: "FileNavigator", files: list[str]) -> None:
    """List directory files."""
    if not files:
        files = ["."]

    files: list[str] = [file if file != "." else fn.path for file in files]
    paths: tuple[Path, ...] = pathify(fn.path, files) 
    for path in paths:
        if path.is_dir():
            files = path.iterdir()
            for file in files:
                print(file)
        elif path.is_file():
            print(path.name)
        else:
            perror("DirectoryOrFileNotFound", filename=path)

@add_command("mk", "make")
def make_files(fn: "FileNavigator", files: list[str]) -> None:
    """Create blank files in given directory."""
    if not files:
        print("Usage: make <filename_1> ...")
        return

    files: tuple[Path, ...] = pathify(fn.path, files) 
    for file in files:
        file_path: Path = (fn.path/file).resolve()
        create_file(file_path)

@add_command("mv", "move")
def move_file(fn: "FileNavigator", files: list[str]) -> None:
    """
    Move file from source to first destination.
    If more destinations passed, moved file now is COPIED to those places
    """
    if len(files) < 2:
        print("Usage: move <source> <destination_1> ...")
        return

    files: tuple[Path, ...] = pathify(fn.path, files)
    source, *destinations = files

    move_anything(source, destinations[0])

    if len(destinations) > 1:
        copy_anything(destinations[0], destinations[1:])

@add_command("cd")
def move_path(fn: "FileNavigator", args: list[str]) -> None:
    """Move from the current directory.""" 
    new_path = " ".join(args)

    if new_path == "..":
        if fn.path == fn.path.anchor:
            print("You're already root.")
        else:
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
