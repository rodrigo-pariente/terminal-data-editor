import argparse
import ast
import json


def smart_cast(value: str) -> any:
    """Cast string to proper type."""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value

def open_json(json_dir: str) -> any:
    """Read JSON file, returns its content."""
    with open(json_dir, "r") as file:
        json_content = json.load(file)
    return json_content

def save_json(json_dir: str, content: any) -> None:
    """Save WHOLE content in a JSON file."""
    with open(json_dir, "w") as file:
        json.dump(content, file, indent=2)

def change_value(data: any, value_path: str, new_value: any) -> any:
    """Change value inside a data structure based in a path."""
    if value_path == "/"
        return new_value

    indexes: list = value_path.split("/")
    indexes = [i if not i.isdigit() else int(i) for i in indexes]

    current = data
    for i in indexes[:-1]:
        current = current[i]
    current[indexes[-1]] = new_value

    return data


parser = argparse.ArgumentParser(prog="JSON Command Line Editor")

parser.add_argument("json_dir", help="JSON file directory's", type=str)
parser.add_argument("path", help="Path of value to be changed", type=str)
parser.add_argument("new_value", help="New value", type=str)

parser.add_argument("-l", "--literal", 
        help="Cast value when writing",
        action="store_true"
        )

args = parser.parse_args()

new_value = args.new_value
if args.literal:
    new_value = smart_cast(new_value)

json_content = open_json(args.json_dir)
new_content = change_value(args.path, json_content, new_value)
save_json(args.json_dir, new_content)
