"""CLI code for running the project."""

import argparse
from pathlib import Path
import os
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator
from widgets.navigator_manager import NavigatorManager
from read_and_write import read_file, write_file
from utils.data_utils import change_data_by_path, smart_cast


def main():
    """Main function."""
    parser = argparse.ArgumentParser(prog="JSON Command Line Editor")

    parser.add_argument(
        "-f",
        "--filename",
        help="JSON file directory's.",
        type=str,
        default=None
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
        "-nl", "--literal_off", 
        help="Not cast value when writing.",
        action="store_true"
    )

    parser.add_argument(
        "-mk", "--make", 
        help="Make file if does not exist.",
        action="store_true"
    )

    args = parser.parse_args()
    path = Path(args.path)

    if args.filename is not None:
        if os.path.isfile(args.filename):
            data = read_file(args.filename)
        else:
            if args.make:
                data = ""
                write_file(args.filename, data)
            else:
                raise SystemExit(f"File {args.filename} does not exist.")
    else:
        data = None

    if args.new_value is None:
        dn: DataNavigator = DataNavigator(data, args.filename, path, (not args.literal_off))
        fn: FileNavigator = FileNavigator()
        nm: NavigatorManager = NavigatorManager([dn], fn)
        nm.run()
    else:
        if not args.literal_off:
            new_value = smart_cast(args.new_value)
        else:
            new_value = args.new_value
        new_content = change_data_by_path(data, path, new_value)
        write_file(args.filename, new_content)


if __name__ == "__main__":
    main()
