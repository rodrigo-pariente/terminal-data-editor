"""CLI code for running the project."""

import argparse
from pathlib import Path
from typing import Any
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator
from widgets.widget_manager import WidgetManager
from read_and_write import read_file
from utils.data_utils import change_data_in_file


def main():
    """Main function."""
    parser = argparse.ArgumentParser(prog="Command Line Data Editor")

    parser.add_argument(
        "-i",
        "--input_files",
        nargs="+",
        help="JSON file directory's.",
        type=str,
        default=None
    )

    parser.add_argument(
        "-s", "--set",
        nargs="+",
        help="New value to be set.",
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
    path: Path = Path(args.path)

    if args.set is None:
        data_navigators: list[DataNavigator] = []
        if args.input_files:
            for filename in args.input_files:
                data: Any = read_file(filename)
                literal: bool = not args.literal_off
                dn = DataNavigator(data, filename, Path(), literal)
                data_navigators.append(dn)
        fn: FileNavigator = FileNavigator()
        wm: WidgetManager = WidgetManager(data_navigators, fn)
        wm.run()

    else:
        change_data_in_file(current_directory=Path.cwd(),
                            files=args.input_files,
                            path=path,
                            new_values=args.set,
                            literal=not args.literal_off)

if __name__ == "__main__":
    main()
