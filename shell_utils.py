"""
Module for some high-level Shell Utilities used in this project.
It's intended to have really secure and reliable shell related functions.
"""
from pathlib import Path
import shutil
import os
from messages import perror


def copy_anything(source: Path, destination: Path) -> bool:
    """
    Copy anything, file or folder into given directory.
    Returns True if file was sucessfully copied, if did not,
    returns False.
    """
    if not Path(destination.parent).is_dir():
        perror("DestinationMustBeDirectory", dirname=str(destination))
        check = create_directories_interface(destination)
        if not destination.is_dir() and check is not None:
            print("Could not copy.")
            return False

    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    elif source.is_file():
        shutil.copy2(source, destination)
    else:
        perror("DirectoryOrFileNotFound", filename=source.name)
        return False
    return True

def create_directory(directory: Path) -> bool:
    """
    Create directory. Returns True if by the end of process, directory 
    exists, if does not, returns False.
    """
    if directory.is_dir():
        perror("DirectoryAlreadyExists", dirname=str(directory))
        return True

    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        perror("PermissionError")    
        return False

def create_directories_interface(directory: Path | list[Path]) -> bool | None:
    """
    User interface for creating a directory when needed for concluding other.
    """
    print("Want to make directory? [y]es, [n]o")
    user_input: str = input(">>>")

    if user_input and user_input.lower()[0] == "y":
        create_dir_value = create_directory(directory)
        return create_dir_value
    return None 

def create_file(file: Path) -> bool:
    """
    Create file. Returns True if by the end of process, file exists,
    if not, returns False.
    """
    if file.is_file():
        perror("FileAlreadyExists", filename=file.name) 
        return True

    try:
        file.touch()
        return True
    except FileNotFoundError:
        perror("DirectoryNotFound", dirname=file.parent)
    except PermissionError:
        perror("PermissionError")
    return False

def delete_anything(file: Path) -> bool:
    """Delete anything, file or folder that is passed."""
    try:
        if file.is_dir():
            shutil.rmtree(file)
            return True
        if file.is_file():
            os.remove(file)
            return True

        perror("DirectoryOrFileNotFound", filename=str(file))
    except PermissionError:
        perror("PermissionError")
    return False

def move_anything(source: Path, destination: Path) -> bool:
    """
    Move anything, file or directory from source into given destination.
    Returns True if process succeded, if did not, returns False.
    """
    if destination.is_dir():
        new_path = (destination / source.name).resolve()
    else:
        new_path = destination

    try:
        source.rename(new_path)
        return True
    except FileNotFoundError:
        perror("DirectoryNotFound", dirname=destination)
        check = create_directories_interface(destination)
        if check is not None:
            move_anything(source, destination)
    except PermissionError:
        perror("PermissionError")
    return False
