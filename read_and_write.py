"""
Module containing functions for reading and writing different file formats.
Add more formats support here.
"""

from collections.abc import Callable
import io
import json
import os
from typing import Any
import toml
import yaml
from messages import perror


SUPPORTED_FORMATS: tuple[str, ...] = (".json", ".toml",".yaml")

read_functions: dict[str, Callable] = {}
write_functions: dict[str, Callable] = {}

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
add_func_to_write: Callable = add_func_to_dict(write_functions)

def read_file(filename: str) -> Any:
    """Read file content if formart is supported."""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        perror("UnsupportedFormats",
                format=ext,
                supported=str(SUPPORTED_FORMATS)
        )
        return None

    try:
        return read_functions[ext](filename)
    except FileNotFoundError:
        perror("FileNotFound", filename=filename)
    except PermissionError:
        perror("PermissionError")
    return None

def write_file(filename: str, content: Any) -> None:
    """write file if format is supported"""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        perror("UnsupportedFormats", format=ext, supported=SUPPORTED_FORMATS)
        return

    try:
        write_functions[ext](filename, content)
    except PermissionError:
        perror("PermissionError")

@add_func_to_read(".json")
def read_json(json_dir: str) -> Any:
    """Read JSON file, return its content."""
    with open(json_dir, "r", encoding="utf8") as file:
        json_content = json.load(file)
    return json_content

@add_func_to_write(".json")
def write_json(json_dir: str, content: Any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_dir, "w", encoding="utf8") as file:
        json.dump(content, file, indent=2)

@add_func_to_read(".toml")
def read_toml(toml_dir: str) -> Any:
    """Read TOML file, return its content"""
    with open(toml_dir, "r", encoding="utf8") as file:
        toml_content = toml.load(file)
    return toml_content

@add_func_to_write(".toml")
def write_toml(toml_dir: str, content: Any) -> None:
    """Save WHOLE content in a TOML file."""
    with io.open(toml_dir, "w", encoding="utf8") as file:
        toml.dump(content, file)

@add_func_to_read(".yaml")
def read_yaml(yaml_dir: str) -> Any:
    """Read YAML file, return its content."""
    with open(yaml_dir, "r", encoding="utf8") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

@add_func_to_write(".yaml")
def write_yaml(yaml_dir: str, content: Any) -> None:
    """Save WHOLE content in a YAML file."""
    with io.open(yaml_dir, "w", encoding="utf8") as file:
        yaml.dump(content, file, indent=4)
