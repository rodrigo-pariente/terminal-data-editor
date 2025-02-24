import io
import json
import os
from typing import Any
import yaml


def read_file(filename: str) -> Any:
    """Read file content if format is supported"""
    ext = os.path.splitext(filename)[1].lower()
    match ext:
        case ".json":
            content = read_json(filename)
        case ".yaml":
            content = read_yaml(filename)
        case _:
            raise SystemExit("Unsupported file format.")
    return content
 
def save_file(filename: str, content: Any) -> Any:
    """Save file if format is supported"""
    ext = os.path.splitext(filename)[1].lower()
    match ext:
        case ".json":
            save_json(filename, content)
        case ".yaml":
            save_yaml(filename, content)
        case _:
            raise SystemExit("Unsupported file format.")

def read_json(json_dir: str) -> Any:
    """Read JSON file, returns its content."""
    with open(json_dir, "r") as file:
        json_content = json.load(file)
    return json_content

def save_json(json_dir: str, content: Any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_dir, "w") as file:
        json.dump(content, file, indent=2)

def read_yaml(yaml_dir: str) -> Any:
    """Read YAML file, returns its content."""
    with open(yaml_dir, "r") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

def save_yaml(yaml_dir: str, content: Any) -> None:
    """Save WHOLE content in a YAML file."""
    with io.open(yaml_dir, "w") as file: #this is a change
        yaml.dump(content, file, indent=4)
