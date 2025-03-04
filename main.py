"""CLI code for running the project."""

import argparse
from pathlib import Path
import sys
from typing import Any
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator
from widgets.widget_manager import WidgetManager
from read_and_write import read_file, write_file
from utils.data_utils import change_data_by_path, smart_cast

def main():
    """Main function."""
    parser = argparse.ArgumentParser(prog="Command Line Data Editor")

    parser.add_argument(
        "-f",
        "--filename",
        nargs="+",
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

    if args.new_value is None:
        data_navigators: list[DataNavigator] = []
        if args.filename:
            for filename in args.filename:
                data: Any = read_file(filename)
                literal: bool = not args.literal_off
                dn = DataNavigator(data, filename, Path(), literal)
                data_navigators.append(dn)
        fn: FileNavigator = FileNavigator()
        wm: WidgetManager = WidgetManager(data_navigators, fn)
        wm.run()

    else:
        if args.filename != 1:
            print("ERROR: For quick changing values in CLI, give one filename.")
            sys.exit(1)
        data = read_file(args.filename[0])
        if not args.literal_off:
            new_value = smart_cast(args.new_value)
        else:
            new_value = args.new_value
        new_content = change_data_by_path(data, path, new_value)
        write_file(args.filename, new_content)


if __name__ == "__main__":
    main()
