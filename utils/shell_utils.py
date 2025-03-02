"""Module for some high-level Shell Utilities used in this project."""

from pathlib import Path
import shutil
import os
from messages import perror


def copy_anything(source: Path, destination: Path) -> None:
    """Copy anything, file or folder into given directory."""
    if not destination.parent.is_dir():
        perror("DestinationMustBeDirectory", dirname=str(destination))
        create_directories_interface(destination)
        if not destination.is_dir():
            print("Could not copy.")
            return

    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    elif source.is_file():
        shutil.copy2(source, destination)
    else:
        perror("DirectoryOrFileNotFound", filename=source.name)

def create_directory(directory: Path) -> None:
    """Create directory in given path."""
    try:
        directory.mkdir(parents=True)
    except FileExistsError:
        perror("DirectoryAlreadyExists", dirname=str(directory))
    except PermissionError:
        perror("PermissionError")

def create_directories_interface(directory: Path | list[Path]) -> None:
    """
    User interface for creating a directory when
    needed for concluding other action.
    """
    print("Want to make directory? [y]es, [n]o")
    user_input: str = input(">>>")

    if user_input and user_input.lower()[0] == "y":
        create_directory(directory)

def create_file(file: Path) -> None:
    """Create blank file."""
    try:
        file.touch(exist_ok=False)
    except FileExistsError:
        perror("FileAlreadyExists", filename=file.name)
    except FileNotFoundError:
        perror("DirectoryNotFound", dirname=file.parent)
    except PermissionError:
        perror("PermissionError")

def delete_anything(file: Path) -> None:
    """Delete anything, file or folder that is passed."""
    try:
        if file.is_dir():
            shutil.rmtree(file)
        else:
            os.remove(file)
    except FileNotFoundError:
        perror("DirectoryOrFileNotFound", filename=str(file))
    except PermissionError:
        perror("PermissionError")

def move_anything(source: Path, destination: Path) -> Path:
    """Move anything, file or directory from source into given destination."""
    if destination.is_dir():
        new_path: Path = (destination / source.name).resolve()
    else:
        new_path: Path = destination

    try:
        source.rename(new_path)
    except FileNotFoundError:
        perror("DirectoryNotFound", dirname=destination)
        create_directories_interface(destination)
        if new_path.parent.is_dir():
            move_anything(source, destination)
        else:
            print("Couldn't move.")
    except PermissionError:
        perror("PermissionError")
    return new_path
