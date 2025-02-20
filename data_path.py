import ast
"""This module can be better organized."""

def smart_cast(value: str) -> any:
    """Cast string to proper type."""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value

def safe_path_split(path: str, int_literal: bool = False) -> list:
    """Safely get path indexes into a list."""
    indexes: list = path.split("/")
    
    if int_literal:
        indexes = [i if not i.isdigit() else int(i) for i in indexes]

    indexes = [i for i in indexes if i != ""]
    return indexes
    
def path_append(path: str, new_index: str | int) -> str:
    """Append new index into given path."""
    if path == "/" or path == "":
        return new_index
    
    if isinstance(new_index, int):
        new_index = str(new_index)

    path: list = safe_path_split(path)
    path.append(new_index)
    path: str = "/".join(path)
    return path

def path_pop(path: str) -> str:
    """Remove last index in given path."""
    path: list = safe_path_split(path)
    path.pop()
    path: str = "/".join(path)
    return path

def get_data_by_path(data: any, path: str) -> any:
    """Get data inside a data structure based in a path."""
    if path == "/" or path == "":
        return data

    indexes = safe_path_split(path, int_literal=True)

    current = data
    for i in indexes:
        current = current[i]
    return current

def change_data_by_path(data: any, path: str, new_data: any) -> any:
    """Change data inside a data structure based in a path."""
    path: list = safe_path_split(path)

    rec_data = get_data_by_path(data, "/".join(path[:-1]))
    rec_data[path[-1]] = new_data

    return data
