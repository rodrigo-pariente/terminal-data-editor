"""
Module containing functions for reading and writing different file formats.

Add support for more file formats here.
"""

from collections.abc import Callable
import io
import json
import logging
import os
from pathlib import Path
from typing import Any

import toml
import yaml

from messages.messages import get_error_message


logger = logging.getLogger(__name__)

SUPPORTED_FORMATS: tuple[str, ...] = (".json", ".toml",".yaml")


read_functions: dict[str, Callable] = {}
write_functions: dict[str, Callable] = {}

def add_func_to_dict(dictionary: dict) -> Callable:
    # Function to create decorators that register functions into dictionaries.
    def add_func(*values) -> Callable:
        def wrapper(func) -> None:
            for value in values:
                dictionary[value] = func
        return wrapper
    return add_func

# decorator to add new read_file functions
add_func_to_read: Callable = add_func_to_dict(read_functions)

# decorator to add new write_file functions
add_func_to_write: Callable = add_func_to_dict(write_functions)

def read_file(filepath: str | Path) -> Any:
    """Read file content if formart is supported."""
    ext: str = os.path.splitext(filepath)[1].lower()

    if not ext:
        ext = "FORMAT_WITHOUT_EXTENSION"

    if ext not in SUPPORTED_FORMATS:
        logger.error(get_error_message(
            "UnsupportedFormat",
            format=ext,
            supported=str(SUPPORTED_FORMATS)
        ))
        return None

    try:
        return read_functions[ext](filepath)
    except FileNotFoundError:
        logger.error(get_error_message("FileNotFound", filepath=filepath))
        raise
    except PermissionError:
        logger.error(get_error_message("PermissionError"))
        raise
    return None

def write_file(filepath: str | Path, content: Any) -> None:
    """Write given content into file if format is supported."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        logger.error(get_error_message(
            "UnsupportedFormat",
            format=ext,
            supported=str(SUPPORTED_FORMATS)
        ))
        return

    try:
        write_functions[ext](filepath, content)
    except PermissionError:
        logger.error(get_error_message("PermissionError"))
        raise

@add_func_to_read(".json")
def read_json(json_filepath: str | Path) -> Any:
    """Read JSON file, return its content."""
    with open(json_filepath, "r", encoding="utf8") as file:
        json_content = json.load(file)
    return json_content

@add_func_to_write(".json")
def write_json(json_filepath: str | Path, content: Any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_filepath, "w", encoding="utf8") as file:
        json.dump(content, file, indent=2)

@add_func_to_read(".toml")
def read_toml(toml_filepath: str | Path) -> Any:
    """Read TOML file, return its content"""
    with open(toml_filepath, "r", encoding="utf8") as file:
        toml_content = toml.load(file)
    return toml_content

@add_func_to_write(".toml")
def write_toml(toml_filepath: str | Path, content: Any) -> None:
    """Save WHOLE content in a TOML file."""
    with io.open(toml_filepath, "w", encoding="utf8") as file:
        toml.dump(content, file)

@add_func_to_read(".yaml")
def read_yaml(yaml_filepath: str | Path) -> Any:
    """Read YAML file, return its content."""
    with open(yaml_filepath, "r", encoding="utf8") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

@add_func_to_write(".yaml")
def write_yaml(yaml_filepath: str | Path, content: Any) -> None:
    """Save WHOLE content in a YAML file."""
    with io.open(yaml_filepath, "w", encoding="utf8") as file:
        yaml.dump(content, file, indent=4)
