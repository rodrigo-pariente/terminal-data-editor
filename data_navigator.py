from data_path import *
from json_utils import *


def data_navigator(data: any, path: str = "", filename: str = "lipsum.json", literal: bool = False) -> None: # too big
    """Terminal data navigator"""
    master_data = data
    while True:
        print(get_data_by_path(data, path), "\n")

        index = input(f"{path}/")

        match index:
            case "\\exit":
                break
        
            case "\\redo":
                data = master_data

            case "\\save":
                save_json(filename, data)
                print(f"Saved at {filename}.")

            case "\\-l":
                literal = False
                print(f"Literal flag turned off.")

            case "\\+l":
                literal = True
                print(f"Literal flag turned on.")

            case "\\":
                new_value = index[1:] if not literal else smart_cast(index[1:])
                change_data_by_path(data, path, new_value)

            case "..":
                if path:
                    path = path_pop(path)
                else:
                    print("ERROR: You are at root level.")

            case:
                path = move(data, path, index)

def move(data: any, path: str, index: str) -> str:
    """Move path based on given index."""
    for i in safe_path_split(index):
        if isinstance(get_data_by_path(data, path), dict):
            if i in get_data_by_path(data, path):
                path = path_append(path, i)
            else:
                print("ERROR: Key not found in dictionary.")
        
        elif isinstance(get_data_by_path(data, path), list):
            if i.isdigit() and 0 <= int(i) < len(get_data_by_path(data, path)):
                path = path_append(path, i)
            else:
                print("ERROR: Invalid list index.")

        else:
            print("ERROR: Cannot navigate into this type.")

    return path

if __name__ == "__main__":
    filename = "json_files/foo.json"
    data = open_json(filename)
    data_navigator(data, filename=filename, literal=True)
