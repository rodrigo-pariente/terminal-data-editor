"""
Module containing data utilities, such as smart_casting for
typefying strings,or acessing nested data based on a path.
"""

import ast
from typing import Any
from pathlib import Path
from read_and_write import read_file, write_file

def smart_cast(value: str) -> Any:
    """Cast string to proper type."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value

def get_data_by_path(data: Any, path: Path) -> Any:
    """Get data inside a data structure based in a path."""
    if path.as_posix() in ("/", ""):
        return data

    indexes: list[str | int] = []
    for part in path.parts:
        if part.isdigit():
            indexes.append(int(part))
        else:
            indexes.append(part)

    current: Any = data
    for i in indexes:
        current: Any = current[i]

    return current

def change_data_by_path(data: Any, path: str | Path, new_data: Any) -> Any:
    """Change data inside a data structure based in a path."""
    path: Path = Path(path)
    if path.as_posix() == ".":
        return new_data

    masked_data: Any = get_data_by_path(data, path.parent)
    masked_data[path.name]: Any = new_data

    return data

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
        print(f"data: {data}")
        data = f"TEMPLATE_{str(type(data)).upper()}"

    return data

def cast_if_true(data: Any, condition: bool) -> Any:
    """Cast given data if condition is true."""
    if not condition:
        return data
    if isinstance(data, list):
        return [smart_cast(i) if isinstance(i, str) else i for i in data]
    return smart_cast(data)

def change_data_in_file(
            current_directory: Path,
            files: list[str],
            path: str,
            new_values: list[str],
            literal: bool) -> None:
    """change value of given data_path in given file"""
    if len(files) != len(new_values):
        if len(new_values) != 1:
            print("Give a new_value per file,\
                or a single value for every file.")
            return
        new_values: list[Any] = new_values * len(files)
    else:
        new_values: list[str] = new_values

    handled_values: list[Any] = cast_if_true(new_values, literal)

    cwd: Path = current_directory
    files: list[Path] = [(cwd / file).resolve() for file in files]

    for i, new_value in enumerate(handled_values):
        read_change_write(files[i], path, new_value)

def read_change_write(file: str, path: Path, new_value: Any) -> None:
    """Change data in file by path"""
    data: Any = read_file(file)
    altered_data: Any = change_data_by_path(data, path, new_value)
    write_file(file, altered_data)
