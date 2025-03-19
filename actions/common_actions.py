"""Actions that can be executed at any moment in the REPL."""

import argparse
from collections.abc import Callable
from copy import deepcopy
import logging
import os
from pathlib import Path
import sys
from typing import Any, TYPE_CHECKING

from actions.action_exceptions import ActionError
from parsing.repl_parser import AttemptToExitError, CommandParser
from read_and_write import read_file, write_file
from messages import change_language
from utils.data_utils import cast_if_true, change_data_in_file, get_template
from widgets.data_editor import DataEditor
from widgets.file_navigator import FileNavigator


if TYPE_CHECKING:
    from widgets.widget_manager import WidgetManager


logger = logging.getLogger(__name__)


common_parser = CommandParser(
    prog="Widget Manager", description="A widget orchestrator.",
    commands_description="Commands to use 🌊"
)

# widget related
# @common_parser.add_args("idiom", choices=["en_US", "pt_BR"])  #NOT IMPLEMENTED YET
# @common_parser.add_cmd("lang")
# def change_lang(de: "DataEditor", parsed: argparse.Namespace) -> None:
#     change_language(parsed.idiom)

@common_parser.add_args(
    "-t", "--tab", nargs="?", default=-1, help="tab of editor to save",
    type=int
)
@common_parser.add_cmd("save")
def save_file(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """Save DataEditor modified data into filename."""
    try:
        de: DataEditor = wm.data_editors[parsed.tab]
    except IndexError:
        raise ActionError("ERROR: Not that many editors opened.")
    
    if de.filename is None:
        filepath: Path = (wm.file_navigator.path / input("filename: ")).resolve() 
        de.filename: Path = filepath
    write_file(de.filename, de.data)
    logger.info(f"Saved at {de.filename}.")

@common_parser.add_args(
    "-t", "--tab", nargs="?", default=-1, help="tab of editor to save",
    type=int
)
@common_parser.add_args("filename", type=str)
@common_parser.add_cmd("saveas")
def save_as(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """Change DataEditor file to another and save."""
    try:
        de: DataEditor = wm.data_editors[parsed.tab]
    except IndexError:
        raise ActionError("ERROR: Not that many editors opened.")

    new_filename: str = parsed.filename
    if de.filename:
        de.filename = (de.filename.parent / new_filename).resolve()
    else:
        de.filename = (wm.file_navigator.path / new_filename).resolve()

    write_file(de.filename, de.data)
    logger.info(f"Saved at {de.filename}.")

@common_parser.add_args(
    "-nl", "--literal_off", action="store_true",
    help="When activated, values will be set as str."
)
@common_parser.add_args(
    "-s", "--set", required=True, nargs="+", type=str,
    help="New values to be set."
)
@common_parser.add_args(
    "-p", "--path", required=True, type=Path,
    help="Path of data to be updated. Ex.: dict_key/0/another_key"
)
@common_parser.add_args(
    "-i", "--input_files", required=True, nargs="+", type=str,
    help="Path of files to be changed."
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

@common_parser.add_args(
    "filepaths", nargs="*", default=[None], help="Path of files to open."
)
@common_parser.add_cmd("edit", help_txt="Open a new editor tab of given file")
def edit_file(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """Starts new DataEditor instance with given file data, if any."""
    filepaths = parsed.filepaths

    new_data_editors: list[DataEditor] = []
    if filepaths != [None]:
        for filepath in filepaths:
            abs_filepath: Path = (wm.file_navigator.path / filepath).resolve()
            data: Any = read_file(abs_filepath)
            new_data_editors.append(DataEditor(data, abs_filepath))
    else:
        new_data_editors.append(DataEditor())

    wm.data_editors.extend(new_data_editors)
    wm.active_widget = wm.data_editors[-1]

@common_parser.add_args(
    "tab", nargs="?", type=int, default=None,
    help="Index of editor tab with data to get template of."
)
@common_parser.add_cmd("gt", "get-template")
def get_template_from_de(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """Get-template of data in editor of given index."""
    if parsed.tab == None:
        try:
            tab_index: int = wm.data_editors.index(wm.active_widget)
        except ValueError:
            return
    else:
        tab_index: int = parsed.editor_tab
    
    try:
        data: Any = deepcopy(wm.data_editors[tab_index].data)
    except IndexError:
        logger.error("Not that many editors opened.")
        return

    template_of_data: Any = get_template(data)
    editor_of_template: DataEditor = DataEditor(template_of_data)

    wm.data_editors.append(editor_of_template)
    wm.active_widget: DataEditor = editor_of_template

@common_parser.add_args(
    "tab", nargs="?", type=int, default=None, help="index of tab to close."
)
@common_parser.add_cmd("close")
def close_data_editor(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """Close current or from given index DataEditor instance."""
    # select the apropriate tab index
    if parsed.tab == None:
        try:
            tab_index: int = wm.data_editors.index(wm.active_widget)
        except ValueError:
            return
    else:
        tab_index: int = parsed.editor_tab

    # close
    try:
        wm.data_editors.pop(tab_index)
    except IndexError:
        raise ActionError("ERROR: Not that many editors opened.")

    # refocus
    if wm.active_widget not in wm.data_editors:
        if wm.data_editors:
            wm.active_widget: DataEditor = wm.data_editors[-1]
        else:
            wm.active_widget: FileNavigator = wm.file_navigator

@common_parser.add_args(
    "tab", nargs="?", default=-1, type=int, help="index of tab to focus."
)
@common_parser.add_cmd("editor")
def focus_data_editor(wm: "WidgetManager", parsed: argparse.Namespace) -> None:
    """Focus WidgetManager in its DataEditor instance."""
    if not wm.data_editors:
        wm.data_editors.append(DataEditor())
    try:
        wm.active_widget = wm.data_editors[parsed.tab]
    except IndexError:
        logger.error("Not that many editors opened.")

@common_parser.add_cmd("explorer")
def focus_file_navigator(wm: "WidgetManager", *_) -> None:
    """Focus WidgetManager in its FileNavigator instance."""
    wm.active_widget = wm.file_navigator

@common_parser.add_cmd("print-tabs", "tabs")
def print_widgets(wm: "WidgetManager", *_) -> None:
    """Print current oppened editors"""
    for i, data_editor in enumerate(wm.data_editors):
        print(f"file: {data_editor.filename} ({i})")

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

@common_parser.add_args("comment", nargs="*")
@common_parser.add_cmd("#")
def commentary(*_) -> None:
    """commentary: does nothing."""
    pass

@common_parser.add_cmd("exit", "quit", "q")
def exit_repl(*_) -> None:
    """Exits the application."""
    sys.exit(0)

@common_parser.add_args("command", nargs="*", )
@common_parser.add_cmd("!")
def shell_commands(_, parsed: argparse.Namespace) -> None:
    """Let user pass shell commands without leaving the application."""
    os.system(" ".join(parsed.command))
