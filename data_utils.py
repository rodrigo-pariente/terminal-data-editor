"""
Module containing data utilities, such as smart_casting for
typefying strings,or acessing nested data based on a path.
"""

import ast
from typing import Any
from pathlib import Path

def smart_cast(value: str) -> Any:
    """Cast string to proper type."""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value

def get_data_by_path(data: Any, path: Path) -> Any:
    """Get data inside a data structure based in a path."""
    posix_path = path.as_posix()
    if posix_path == "/" or posix_path == "":
        return data

    indexes = [int(part) if part.isdigit() else part for part in path.parts]
    current = data
    for i in indexes:
        current = current[i]

    return current

def change_data_by_path(data: Any, path: str, new_data: Any) -> Any:
    """Change data inside a data structure based in a path."""
    masked_data = get_data_by_path(data, path.parent)
    masked_data[path.name] = new_data 

    return data
