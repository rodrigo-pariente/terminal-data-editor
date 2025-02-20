import argparse
from data_path import *
from json_utils import *

def main():
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
    new_content = change_data_by_path(json_content, args.path, new_value)
    save_json(args.json_dir, new_content)


if __name__ == "__main__":
    main()
