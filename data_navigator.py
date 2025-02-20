from data_path import *
from json_utils import *


def data_navigator(data: any, path: str = ""):
    """Terminal data navigator"""
    while True:
        print(get_data_by_path(data, path))

        index = input(f"{path}/")

        if index == "exit":
            break

        elif index == "..":
            if path:
                path = path_pop(path)
            else:
                print("ERROR: You are at root level.")

        else:
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
    data = open_json("json_files/foo.json")
    data_navigator(data)
