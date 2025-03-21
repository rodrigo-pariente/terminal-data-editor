"""
Module for storing data utilities used in this project.

This module provides fundamental functions like `smart_cast`, for 
inteligent type conversions, and `change_data_by_path`, for updating 
nested data structures.
"""

import ast
from itertools import repeat
import logging
from typing import Any, Callable
from pathlib import Path

from messages.messages import error_msg
from read_and_write import read_file, write_file


logger = logging.getLogger(__name__)


def smart_cast(value: str) -> Any:
    """Do a intelligent type conversion of given value."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value

def cast_if_true(data: Any, condition: bool) -> Any:
    """If condition is met, data will be casted and returned."""
    if not condition:
        return data
    if isinstance(data, list):
        return [smart_cast(i) if isinstance(i, str) else i for i in data]
    return smart_cast(data)

def get_data_by_path(data: Any, data_path: Path) -> Any:
    """Get data inside a data structure based in a path."""
    if data_path.as_posix() in ("/", ""):
        return data

    indexes: list[str | int] = []
    for index in data_path.parts:
        if index.isdigit():
            indexes.append(int(index))
        else:
            indexes.append(index)

    current: Any = data
    for index in indexes:
        try:
            current: Any = current[index]
        except (KeyError, TypeError) as e:
            # for better error message # this isn't the place
            if isinstance(index, str):
                index = f'"{index}"'
            if isinstance(current, str):
                current = f'"{current}"'

            message = error_msg["InvalidIndex"].format(index=index, data=current)
            raise IndexError(message) from e

    return current

def change_data_by_path(
    data: Any,
    data_path: Path,
    new_data: Any
) -> Any:
    """Change data inside a data structure based in a path."""
    if data_path.as_posix() == ".":
        return new_data

    masked_data: Any = get_data_by_path(data, data_path.parent)

    last_index: int | str
    if data_path.name.isdigit():
        last_index = int(data_path.name)
    else:
        last_index = data_path.name

    try:
        masked_data[last_index]: Any = new_data
    except KeyError as e: # this is ugly <-----------
        if isinstance(masked_data, dict) and isinstance(last_index, int):
            masked_data[str(last_index)] = new_data
        else:
            raise

    return data

def change_data_in_file(
    filepaths: list[Path],
    data_path: str,
    new_values: list[Any],
) -> None:
    """change value of given data_path in given file"""
    if len(filepaths) != len(new_values):
        if len(new_values) != 1:
            logger.error(
                "Give a new_value per file or a single value for every file."
            )
            return
        new_values = repeat(new_values[0])

    for i, filepath in enumerate(filepaths):
        read_change_write(filepath, data_path, new_values[i])

def get_template(data: Any):
    """Makes template out of given data."""
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                get_template(item)
            else:
                data[i] = f"TEMPLATE_{str(type(item)).upper()}"

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                get_template(value)
            else:
                data[key] = f"TEMPLATE_{str(type(value)).upper()}"

    else:
        data = f"TEMPLATE_{str(type(data)).upper()}"

    return data

def read_change_write(
    filepath: Path,
    data_path: Path,
    new_value: Any
) -> None:
    """Change data in file by path"""
    data: Any = read_file(filepath)
    updated_data: Any = change_data_by_path(data, data_path, new_value)
    write_file(filepath, updated_data)

def iter_data(
    data: Any,
    dict_answer: Callable,
    list_answer: Callable,
    data_answer: Callable,
) -> Any:

    if isinstance(data, dict):
        return {
            k: iter_data(v, dict_answer, list_answer, data_answer)
            if isinstance(v, (list, dict))
            else dict_answer(k, v)
            for k, v in data.items()
        }

    if isinstance(data, list):
        return [
            iter_data(i, dict_answer, list_answer, data_answer)
            if isinstance(i, (dict, list))
            else list_answer(i, item)
            for i, item in enumerate(data)
        ]

    return data_answer(data)