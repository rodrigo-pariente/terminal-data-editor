"""Module containing functions for handling data serial files."""

from collections.abc import Callable
import io
import json
import os
from typing import Any
import yaml
from messages import perror


SUPPORTED_FORMATS: tuple[str, ...] = (".json", ".yaml")

read_functions: dict[str, Callable[str, Any]] = {}
save_functions: dict[str, Callable[str, Any]] = {}

def add_func_to_dict(dictionary: dict) -> Callable:
    """
    Helper function to create decorators that 
    register functions into dictionaries
    """
    def add_func(*values) -> Callable:
        def wrapper(func) -> None:
            for value in values:
                dictionary[value] = func
        return wrapper
    return add_func

add_func_to_read: Callable = add_func_to_dict(read_functions)
add_func_to_save: Callable = add_func_to_dict(save_functions)

def read_file(filename: str) -> Any:
    """Read file content if formart is supported."""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        perror("UnsupportedFormats", format=ext, supported=SUPPORTED_FORMATS)
        return None

    try:
        return read_functions[ext](filename)
    except FileNotFoundError:
        perror("FileNotFound", filename=filename)
    except PermissionError:
        perror("PermissionError") # is this really possible?
    return None

def save_file(filename: str, content: Any) -> None:
    """Save file if format is supported"""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        perror("UnsupportedFormats", format=ext, supported=SUPPORTED_FORMATS)
        return
    try:
        save_functions[ext](filename, content)
    except PermissionError:
        perror("PermissionError")

@add_func_to_read(".json")
def read_json(json_dir: str) -> Any:
    """Read JSON file, returns its content."""
    with open(json_dir, "r", encoding="utf8") as file:
        json_content = json.load(file)
    return json_content

@add_func_to_save(".json")
def save_json(json_dir: str, content: Any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_dir, "w", encoding="utf8") as file:
        json.dump(content, file, indent=2)

@add_func_to_read(".yaml")
def read_yaml(yaml_dir: str) -> Any:
    """Read YAML file, returns its content."""
    with open(yaml_dir, "r", encoding="utf8") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

@add_func_to_save(".yaml")
def save_yaml(yaml_dir: str, content: Any) -> None:
    """Save WHOLE content in a YAML file."""
    with io.open(yaml_dir, "w", encoding="utf8") as file:
        yaml.dump(content, file, indent=4)
