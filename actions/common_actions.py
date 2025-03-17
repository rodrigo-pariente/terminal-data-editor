"""Actions that can be executed at any moment in the REPL."""

import argparse
from collections.abc import Callable
from copy import deepcopy
import logging
import os
from pathlib import Path
import sys
from typing import Any, TYPE_CHECKING

from parsing.repl_parser import AttemptToExitError, CommandParser
from read_and_write import read_file
from utils.data_utils import cast_if_true, change_data_in_file, get_template
from widgets.data_editor import DataEditor
from widgets.file_navigator import FileNavigator


if TYPE_CHECKING:
    from widgets.widget_manager import WidgetManager


logger = logging.getLogger(__name__)

common_parser = CommandParser(
    prog="Widget Manager", description="A widget orchestrator.",
    add_help=False, commands_description="Commands to use 👩‍💻"
)

# widget related
@common_parser.add_args(  # see if there's better way to do that
    "-nl", "--literal_off",
    help=(
        "When activated, types won't be casted "
        "and values will be set as str."
    ),
    action="store_true"
)
@common_parser.add_args(
    "-s", "--set",
    required=True,
    nargs="+",
    help="New values to be set.",
    type=str
)
@common_parser.add_args(
    "-p", "--path",
    required=True,
    help="Path of data to be updated. Ex.: dict_key/0/another_key",
    type=str
)
@common_parser.add_args(
    "-i", "--input_files",
    required=True,
    nargs="+",
    help="Path of files to be changed.",
    type=str
)
@common_parser.add_cmd("change")
def change_value_in_file(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """
    Update the data of files (-i) in give data_path (-p)
    with the new_values (-s).
    """
    filepaths: list[Path] = [
        (wm.file_navigator.path / filepath).resolve()
        for filepath in parsed.input_files
    ]

    change_data_in_file(
        filepaths=filepaths,
        data_path=parsed.path,
        new_values=cast_if_true(parsed.set, not parsed.literal_off)
    )

@common_parser.add_args("filepaths", nargs="+", help="Path of files to open.")
@common_parser.add_cmd("edit", help_txt="Open a new editor tab of given file")
def edit_file(wm: "WidgetManager", parsed: argparse.Namespace) -> None:  # let have default value
    """Starts new DataEditor instance with given file data, if any."""
    filepaths = parsed.filepaths
    new_data_editors: list[DataEditor] = []
    if filepaths[0] != "null":
        for filepath in filepaths:
            abs_filepath: Path = (wm.file_navigator.path / filepath).resolve()
            data: Any = read_file(abs_filepath)
            new_data_editors.append(DataEditor(data, abs_filepath))
    else:
        new_data_editors.append(DataEditor())

    wm.data_editors.extend(new_data_editors)
    wm.active_widget = wm.data_editors[-1]

@common_parser.add_args(
    "editor_tab",
    help="Index of editor tab with data to get template of.",
    type=int
)
@common_parser.add_cmd("gt", "get-template")
def get_template_from_de(wm: "WidgetManager", parsed: argparse.Namespace) -> None:  # see integ
    """Get-template of data in editor of given index."""
    try:
        data: Any = deepcopy(wm.data_editors[parsed.editor_tab].data)
    except IndexError:
        logger.error("Not that many editors opened.")
        return

    template_of_data: Any = get_template(data)
    editor_of_template: DataEditor = DataEditor(template_of_data)

    wm.data_editors.append(editor_of_template)
    wm.active_widget: DataEditor = editor_of_template

@common_parser.add_args("tab", type=int, help="index of tab to close.")
@common_parser.add_cmd("close")
def close_data_editor(wm: "WidgetManager", parsed: argparse.Namespace) -> None:  # see integ
    """Close current or from given index DataEditor instance."""
    # Close
    try:
        wm.data_editors.pop(parsed.tab)
    except IndexError:
        print("ERROR: Not that many editors opened.")
        return

    # Refocus
    if wm.active_widget not in wm.data_editors:
        if wm.data_editors:
            wm.active_widget: DataEditor = wm.data_editors[-1]
        else:
            wm.active_widget: FileNavigator = wm.file_navigator

@common_parser.add_args("tab", type=int, help="index of tab to focus.")
@common_parser.add_cmd("editor")
def focus_data_editor(wm: "WidgetManager", parsed: argparse.Namespace) -> None:  # see integ
    """Focus WidgetManager in its DataEditor instance."""
    wm.data_editors.append(DataEditor())
    try:
        wm.active_widget = wm.data_editors[parsed.tab]
    except IndexError:
        print("ERROR: Not that many editors opened.")

@common_parser.add_cmd("explorer")
def focus_file_navigator(wm: "WidgetManager", *_) -> None:
    """Focus WidgetManager in its FileNavigator instance."""
    wm.active_widget = wm.file_navigator

@common_parser.add_cmd("print-tabs", "tabs")
def print_widgets(wm: "WidgetManager", *_) -> None:
    """Print current oppened editors"""
    for i, data_editor in enumerate(wm.data_editors):
        print(f"\nindex: {i}\t file: {data_editor.filename} ")

@common_parser.add_cmd("help")
def print_help(wm: "WidgetManager", *_) -> None:
    """print this help message."""
    wm.parser.print_help()
    wm.active_widget.parser.print_help()

# unespecific
@common_parser.add_cmd("cls", "clear")
def clear_screen(*_) -> None:
    """Clean the screen without leaving the REPL"""
    os.system("cls" if os.name == "nt" else "clear")

@common_parser.add_args(" ", nargs="+")
@common_parser.add_cmd("#")
def commentary(*_) -> None:
    """commentary: does nothing."""
    pass

@common_parser.add_cmd("exit", "quit", "q")
def exit_repl(*_) -> None:
    """Exits the application."""
    sys.exit(0)

@common_parser.add_args("command", nargs="+")
@common_parser.add_cmd("!")
def shell_commands(_, parsed: argparse.Namespace) -> None:
    """Let user pass shell commands without leaving the application."""
    os.system(" ".join(parsed.command))
