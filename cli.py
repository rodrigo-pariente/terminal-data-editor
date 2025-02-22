import argparse
from data_navigator import DataNavigator
from file_utils import *
from path_utils import *


def die(msg: str) -> None:
    print(f"ERROR: {msg}")
    exit(1) # needs better error handling

def main():
    parser = argparse.ArgumentParser(prog="JSON Command Line Editor")

    parser.add_argument(
        "action",
        help="[c]hange in <filename> value from <path> to <new_value>. \n  \
        [n]avigate in <filename> data starting from <path>.", # u call that help?
        type=str
    )

    parser.add_argument("filename", help="JSON file directory's", type=str)

    parser.add_argument(
        "-p", "--path",
        help="Path of value to be changed",
        default="", 
        type=str
    )

    parser.add_argument( # must be given if action not n
        "-nv", "--new_value",
        help="New value",
        type=str,
        default=None
    )

    parser.add_argument(
        "-l", "--literal", 
        help="Cast value when writing",
        action="store_true"
    )

    args = parser.parse_args()

    action = args.action[0].lower()
    data = open_json(args.filename)

    match action:
        case "c":
            if args.new_value != None:
                if args.literal:
                    new_value = smart_cast(args.new_value)
                else:
                    new_value = args.new_value
            else:
                 die("Need new_value to make a change.")

            new_content = change_data_by_path(data, args.path, new_value)
            save_json(args.filename, new_content)
        
        case "n":
            DataNavigator(data, args.path, args.filename, args.literal)
        
        case _:
            die("USAGE: [action] <filename> (args...)") # that does not help either


if __name__ == "__main__":
    main()
