"""Common actions between navigators."""

from argparse import ArgumentError
from collections.abc import Callable
import os
from pathlib import Path
import sys
from typing import Any, TYPE_CHECKING

from parsing import FunctionArgumentParser as FuncArgParser
from read_and_write import read_file
from utils.data_utils import get_template, change_data_in_file
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator


if TYPE_CHECKING:
    from widgets.widget_manager import WidgetManager

common_commands: dict[str, Callable] = {}

def add_command(*commands_list: tuple[str, ...]) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(action):
        for command in commands_list:
            common_commands[command] = action
    return wrapper

# widget related
@add_command("change")
def change_value_in_file(wm: "WidgetManager", args: list[str]) -> None:
    """change value of given data_path in given file"""
    parser = FuncArgParser("change",
                           "Change value of given data_path in given file.")
    parser.add_argument("-i", "--input_files",
                        required=True,
                        nargs="+",
                        help="Files with data to change.",
                        type=str
    )
    parser.add_argument("-p", "--path",
                        required=True,
                        help="Data_path of data to change",
                        type=str
    )
    parser.add_argument("-s", "--set",
                        required=True,
                        nargs="+",
                        help="New value to be set.",
                        type=str
    )
    parser.add_argument("-nl", "--not_literal",
                        help="Not Literal: do not cast any given values.",
                        action="store_true"
    )
    try:
        parsed = parser.safe_parse_args(args)
    except ArgumentError:
        return

    change_data_in_file(wm.file_navigator.path,
                        parsed.input_files,
                        parsed.path,
                        parsed.set,
                        not parsed.not_literal)

@add_command("edit")
def edit_file(wm: "WidgetManager", file: list[str]) -> None:
    """Open file in DataNavigator instance"""
    if file:
        filename: str = " ".join(file)
        abs_filename: Path = (wm.file_navigator.path / filename).resolve()
        data: Any = read_file(abs_filename)
        dn: DataNavigator = DataNavigator(data, abs_filename)
    else:
        dn: DataNavigator = DataNavigator()

    wm.data_navigators.append(dn)
    wm.active_widget: DataNavigator = wm.data_navigators[-1]

@add_command("gt", "get-template")
def get_template_from_dn(wm: "WidgetManager", args: list[str]) -> None:
    """Get template model of data in current editor."""
    if not args and isinstance(wm.active_widget, DataNavigator):
        template_from_data: Any = get_template(wm.active_widget.data)
    elif len(args) == 1 and args[0].isdigit():
        index: int = int(args[0])
        try:
            template_from_data: Any = get_template(wm.data_navigators[index])
        except IndexError:
            print("ERROR: Not that many editors opened.")
            return
    else:
        print("Usage: get-template <editor_tab>")
        return
    editor_of_template: DataNavigator = DataNavigator(template_from_data)
    wm.data_navigators.append(editor_of_template)
    wm.active_widget: DataNavigator = editor_of_template

@add_command("close")
def close_data_navigator(wm: "WidgetManager", args: list[str]) -> None:
    """Close current or from given index DataNavigator instance."""
    # Close
    if not args and isinstance(wm.active_widget, DataNavigator):
        wm.data_navigators.remove(wm.active_widget)
    elif len(args) == 1 and args[0].isdigit():
        try:
            index: int = int(args[0])
            wm.data_navigators.pop(index)
        except IndexError:
            print("ERROR: Not that many editors opened.")
            return
    else:
        print("Usage: close [tab_index]")
        return

    # Refocus
    if wm.active_widget not in wm.data_navigators:
        if wm.data_navigators:
            wm.active_widget: DataNavigator = wm.data_navigators[-1]
        else:
            wm.active_widget: FileNavigator = wm.file_navigator

@add_command("explorer")
def focus_file_navigator(wm: "WidgetManager", *_) -> None:
    """Focus WidgetManager in its FileNavigator instance."""
    wm.active_widget = wm.file_navigator

@add_command("editor")
def focus_data_navigator(wm: "WidgetManager", args: list[str]) -> None:
    """Focus WidgetManager in its DataNavigator instance."""
    if not args:
        if not wm.data_navigators:
            wm.data_navigators.append(DataNavigator())
        index: int = 0
    elif len(args) == 1 and args[0].isdigit() and wm.data_navigators:
        index: int = int(args[0])
    else:
        print("Usage: editor [index]")
        return

    try:
        wm.active_widget = wm.data_navigators[index]
    except IndexError:
        print("ERROR: Not that many editors opened.")

@add_command("print-tabs", "tabs")
def print_widgets(wm: "WidgetManager", *_) -> None:
    """Print current oppened editors"""
    for i, data_navigator in enumerate(wm.data_navigators):
        print(f"\nindex: {i}\t file: {data_navigator.filename} ")

# unespecific
@add_command("cls", "clear")
def clear_screen(*_) -> None:
    """Clean the screen without leaving the REPL"""
    os.system("cls" if os.name == "nt" else "clear")

@add_command("exit", "quit", "q")
def exit_repl(*_) -> None:
    """Exits the application."""
    sys.exit(0)

@add_command("!")
def shell_commands(_, args: list[str]) -> None:
    """Let user pass shell commands without leaving the application."""
    if not args:
        print("Usage: ! <shell command>")
        return
    os.system(" ".join(args))
