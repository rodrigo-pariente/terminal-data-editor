"""
Main logic for running the project.

This program can be executed as a CLI tool or in an interactive REPL environment.

### Example usage as a CLI:

$ python3 ./main.py -i path/to/file.json -p path/to/nested/data -s new_value

This will access the input file, navigate to the specified data path,  
and set the `new_value`.

### Example usage in REPL mode:

$ python3 ./main.py -i path/to/file.json

#### REPL commands:
- `ls`  
  Displays the data inside the file.

- `cd path/to/nested/data`  
  Moves the navigator's `data_path` to the specified nested location.

- `set new_value`  
  Updates the data at the current path with `new_value`.

- `save`  
  Saves the updated data back to `file.json`.

- `exit`  
  Exits the program.

"""

import argparse
from pathlib import Path
import sys
from typing import Any

from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator
from widgets.widget_manager import WidgetManager
from read_and_write import read_file
from utils.data_utils import cast_if_true, change_data_in_file


def main():
    """CLI Logic along with the REPL ambient composition."""
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
    literal: bool = not args.literal_off

    if args.set is None:
        data_navigators: list[DataNavigator] = []
        if args.input_files:
            # for each file given, an editor of it will be opened.
            for filename in args.input_files: 
                data: Any = read_file(filename)
                dn = DataNavigator(data, filename, Path(), literal)
                data_navigators.append(dn)
        # the REPL ambient is composed by a file explorer (>>> explorer)
        # and tabs of data editors (>>> editor)
        fn: FileNavigator = FileNavigator()
        wm: WidgetManager = WidgetManager(data_navigators, fn)
        wm.run()

    else:
        filepaths: list[Path] = [
            (Path.cwd() / filepath).resolve()
            for filepath in args.input_files
        ]

        change_data_in_file(
            filepaths=filepaths,
            data_path=path,
            new_values=cast_if_true(args.set, not args.literal_off)
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

