"""
Module containing data utilities, such as smart_casting for
typefying strings,or acessing nested data based on a path.
"""

import ast
from typing import Any
from pathlib import Path


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

def change_data_by_path(data: Any, path: Path, new_data: Any) -> Any:
    """Change data inside a data structure based in a path."""
    if path.as_posix() == ".":
        return new_data

    masked_data: Any = get_data_by_path(data, path.parent)
    masked_data[path.name]: Any = new_data

    return data

def template_from_data(data: Any):
    """Makes template out of given data."""
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                template_from_data(item)
            else:
                data[i] = f"TEMPLATE_{str(type(item)).upper()}"

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                template_from_data(value)
            else:
                data[key] = f"TEMPLATE_{str(type(value)).upper()}"

    else:
        print(f"data: {data}")
        data = f"TEMPLATE_{str(type(data)).upper()}"

    return data
