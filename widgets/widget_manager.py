"""
Widget Manager module, for holding a higher class that orchestrate
the REPL ambient.
"""

from pprint import pprint

import argparse
import logging
import sys

from actions.action_exceptions import ActionError
from actions.common_actions import common_parser
from widgets.data_editor import DataEditor
from widgets.file_navigator import FileNavigator
from parsing.lexer import pre_parser
from parsing.repl_parser import AttemptToExitError


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
                pre_parsed: list[str] = pre_parser(line)
            except (KeyboardInterrupt):
                sys.exit(0)
            except (SyntaxError, IndexError, ValueError) as e:
                if isinstance(e, SyntaxError):
                    message = "Bad syntax."
                    logger.error(message)
                logger.debug(e)
                continue

            # try to parse with widget_manager parser first
            try: 
                parsed: argparse.Namespace = self.parser.parse_args(
                    pre_parsed, suppress_argument_error=False
                )
                widget = self
            
            # if fails by invalid choice given,
            # try to parse with active_widget parser
            except argparse.ArgumentError as e:
                if e.message.startswith("invalid choice: "):
                    try:
                        parsed = self.active_widget.parser.parse_args(pre_parsed)
                        widget = self.active_widget
                    # if it fails again, the user input was invalid
                    except AttemptToExitError:
                        continue
                else:
                    logger.error(e)
                    continue
            except AttemptToExitError:
                continue

            # if given input has a widget-action, execute it
            action: Callable | None = vars(parsed).pop("func", None)
            if action:
                try:
                    kwargs: dict = vars(parsed)
                    action(widget, **kwargs)
                except ActionError as e:
                    logger.error(e)
