import json


def open_json(json_dir: str) -> any:
    """Read JSON file, returns its content."""
    with open(json_dir, "r") as file:
        json_content = json.load(file)
    return json_content

def save_json(json_dir: str, content: any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_dir, "w") as file:
        json.dump(content, file, indent=2)
