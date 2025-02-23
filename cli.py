import argparse
from data_navigator import DataNavigator
from file_utils import *
from path_utils import *
import os


def main():
    parser = argparse.ArgumentParser(prog="JSON Command Line Editor")

    parser.add_argument(
        "filename",
        help="JSON file directory's.",
        type=str
    )

    parser.add_argument(
        "-nv", "--new_value",
        help="New value.",
        type=str,
        default=None
    )

    parser.add_argument(
        "-p", "--path",
        help="Path of value to be changed.",
        default="", 
        type=str
    )

    parser.add_argument(
        "-l", "--literal", 
        help="Cast value when writing.",
        action="store_true"
    )

    parser.add_argument(
        "-mk", "--make", 
        help="Make file if does not exist.",
        action="store_true"
    )

    args = parser.parse_args()

    if os.path.isfile(args.filename):
        data = open_file(args.filename)
        print(f"data: {data}")
    else:
        if args.make:
            data = ""
            save_file(args.filename, data)
        else:
            raise SystemExit(f"File {args.filename} does not exist.")
    
    if args.new_value == None:
        dn = DataNavigator(data, args.path, args.filename, args.literal)
        dn.run()
    else:
        if args.literal:
            new_value = smart_cast(args.new_value)
        else:
            new_value = args.new_value
        new_content = change_data_by_path(data, args.path, new_value)
        save_file(args.filename, new_content)


if __name__ == "__main__":
    main()
