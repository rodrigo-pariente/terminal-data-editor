"""FileNavigator REPL actions"""
# make directory, filepath, abs_filepath use consistent
# make resolve use consistent
# solve default values in positional arguments
import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any, TYPE_CHECKING

from messages import perror
from utils.shell_utils import (
    copy_anything, delete_anything, move_anything, create_file,
    create_directory
)
from utils.data_utils import get_template
from read_and_write import read_file, write_file
from parsing.repl_parser import CommandParser


if TYPE_CHECKING:
    from widgets.file_navigator import FileNavigator


file_navigator_parser = CommandParser(
    prog="File Navigator", description="A widget to explore file",
    add_help=False, commands_description="Commands to navigate 🧭"
)

def resolve_paths(main_path: Path, relatives: list[str]) -> tuple[Path, ...]:
    """Unify paths with a master path if they're relatives."""
    return tuple((main_path / relative).resolve() for relative in relatives)

@file_navigator_parser.add_args("destinations", nargs="+")
@file_navigator_parser.add_args("source", type=str)
@file_navigator_parser.add_cmd("copy", "cp")
def copy_files(fn: "FileNavigator", parsed: argparse.Namespace) -> None: # add filters
    """Copy file from source into given destinations."""
    destinations: tuple[Path, ...]
    destinations = resolve_paths(fn.path, parsed.destinations)
    source: Path = resolve_paths(fn.path, [parsed.source])[0]

    for destination in destinations:
        copy_anything(source, destination)

@file_navigator_parser.add_args("directories", nargs="+")
@file_navigator_parser.add_cmd("mkdir")
def create_directories(fn: "FileNavigator", parsed: argparse.Namespace) -> None:
    """Create empty directories in given directory."""
    directories: tuple[Path, ...] = resolve_paths(fn.path, parsed.directories)
    for directory in directories:
        create_directory(directory)

@file_navigator_parser.add_args("filepaths", nargs="+")
@file_navigator_parser.add_cmd("del", "rm")
def delete_files(fn: "FileNavigator", parsed: argparse.Namespace) -> None:
    """Delete file or folder from current or given directory."""
    filepaths: tuple[Path, ...] = resolve_paths(fn.path, parsed.filepaths)
    for filepath in filepaths:
        delete_anything(filepath)

@file_navigator_parser.add_args("template_path", type=str)
@file_navigator_parser.add_args("filepath", type=str)
@file_navigator_parser.add_cmd("xt", "extract-template")
def extract_template_from_file(
    fn: "FileNavigator",
    parsed: argparse.Namespace
) -> None:
    """Extract template of data from given file into a new template_file"""
    abs_filepath: Path = (fn.path / parsed.filepath).resolve()
    template_filepath: Path = Path(fn.path / parsed.template_path).resolve()

    data: Any = read_file(abs_filepath)
    template: Any = get_template(data)

    write_file(template_filepath, template)

@file_navigator_parser.add_args("filepaths", nargs="+", default=["."])
@file_navigator_parser.add_cmd("list", "ls")  # does not work ^^^^^^^^
def list_files(fn: "FileNavigator", parsed: argparse.Namespace) -> None:
    """List directory files. Can list multiple directories at once."""
    targets: list[str] = parsed.filepaths

    filepaths: list[str]
    filepaths = [target if target != "." else fn.path for target in targets]

    abs_filepaths: tuple[Path, ...] = resolve_paths(fn.path, filepaths)
    for filepath in abs_filepaths:
        if filepath.is_dir():
            for item in filepath.iterdir():
                print(item)
        elif filepath.is_file():
            print(filepath.name)  # to-do: make it prettier
        else:
            perror("DirectoryOrFileNotFound", filename=filepath)

@file_navigator_parser.add_args("filepaths", nargs="+")
@file_navigator_parser.add_cmd("mk", "make")
def make_files(fn: "FileNavigator", parsed: argparse.Namespace) -> None:
    """Create blank files in given directory."""
    abs_filepaths: tuple[Path, ...] = resolve_paths(fn.path, parsed.filepaths)
    for filepath in abs_filepaths:
        create_file(filepath)

@file_navigator_parser.add_args("destinations", nargs="+")
@file_navigator_parser.add_args("source", type=str)
@file_navigator_parser.add_cmd("mv", "move")
def move_file(fn: "FileNavigator", parsed: argparse.Namespace) -> None:
    """
    Move file from source to first destination.
    If more destinations passed, moved file now is COPIED to those places
    """
    destinations: tuple[Path, ...]
    destinations = resolve_paths(fn.path, parsed.destinations)
    source: Path = resolve_paths(fn.path, [parsed.source])[0]

    new_source_path: Path = move_anything(source, destinations[0])

    if len(destinations) > 1:
        for destination in destinations[1:]:
            copy_anything(new_source_path, destination)

@file_navigator_parser.add_args("directory", type=str)
@file_navigator_parser.add_cmd("cd")
def change_dir(fn: "FileNavigator", parsed: argparse.Namespace) -> None:
    """Move from the current directory.""" 

    if parsed.directory == "..":
        fn.path = fn.path.parent
        return

    potential_path: Path = (fn.path / parsed.directory).resolve()
    if potential_path.is_dir():
        fn.path = potential_path
    else:
        perror("DirectoryNotFound", dirname=potential_path)

@file_navigator_parser.add_cmd("pwd")
def show_current_directory(fn: "FileNavigator", *_) -> None:
    """Shows current working directory."""
    print(f"path: {fn.path}")
