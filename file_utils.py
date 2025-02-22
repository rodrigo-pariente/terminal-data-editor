import json
from typing import Any


def open_json(json_dir: str) -> Any:
    """Read JSON file, returns its content."""
    with open(json_dir, "r") as file:
        json_content = json.load(file)
    return json_content

def save_json(json_dir: str, content: Any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_dir, "w") as file:
        json.dump(content, file, indent=2)
