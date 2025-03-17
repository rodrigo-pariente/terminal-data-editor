"""
Widget Manager module, for holding a higher class that orchestrate
the REPL ambient.
"""

import argparse
import logging
import sys

from actions.common_actions import common_parser
from widgets.data_editor import DataEditor
from widgets.file_navigator import FileNavigator
from parsing.lexer import lexer
from parsing.repl_parser import AttemptToExitError, parse_and_execute


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WidgetManager:
    """Object for organizing and integrating navigator widgets."""
    def __init__(
        self,
        data_editors: list[DataEditor],
        file_navigator: FileNavigator
    ) -> None:
        self.data_editors = data_editors
        self.file_navigator = file_navigator
        self.parser = common_parser

        # by default, it initializes focused in the file_navigator
        self.active_widget: DataEditor | FileNavigator = self.file_navigator

        # if there's a properly setted data_editor, it's then focused in
        for data_editor in self.data_editors:
            if data_editor.filename is not None:
                self.active_widget = data_editor
                break

    def run(self) -> None:
        """Execute the REPL ambient"""
        while True:
            # capture of user input
            try:
                line = input(">>>")
                pre_parsed: list[str]= lexer(line)
                command = pre_parsed[0]
                args = pre_parsed[1:]
            except (
                SyntaxError, IndexError, ValueError, KeyboardInterrupt
            ) as e:
                if isinstance(e, KeyboardInterrupt):
                    sys.exit(0)
                if isinstance(e, SyntaxError):
                    error_msg = "Bad syntax."
                    logger.error(error_msg)
                logger.warn(e)  # to-do: let debug log this
                continue

            # select the parser associated with command
            if command in self.parser.commands.choices:
                selected_widget = self
            elif command in self.active_widget.parser.commands.choices:
                selected_widget = self.active_widget
            else:
                logger.error("Invalid command.")
                continue
            
            try:
                parse_and_execute(selected_widget, line)
            except AttemptToExitError as e:
                continue
