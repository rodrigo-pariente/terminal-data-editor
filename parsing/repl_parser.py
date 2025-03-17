"""Module for storing argparse patches for a REPL ambient instead of CLI."""

import argparse
import logging
import sys
from typing import Callable, Self, TYPE_CHECKING

from parsing.lexer import lexer


logger = logging.getLogger(__name__)

class AttemptToExitError(Exception):
    """Error to be raised whenever argparse try to exit the program."""
    pass

class REPLHelpFormater(argparse.HelpFormatter):
    """A help formatter for REPLParser."""
    def _format_usage(self, usage, actions, groups, prefix):
        """Hiding program name for the REPL ambient"""
        usage = super(REPLHelpFormater, self)._format_usage(
            usage, actions, groups, prefix
        )
        return usage.replace(f"{self._prog} ", "")

class CommandParser(argparse.ArgumentParser):
    """ArgumentParser for the custom REPL commands."""
    def __init__(
        self,
        add_help: bool = True,
        add_commands: bool = True,
        commands_title: str | None = None,
        commands_description: str = "",
        commands_help: str = "",
        exit_on_error: bool = False,
        *args, **kwargs
    ) -> None:
        """
        Args:
            add_help: Add default help option.
            add_commands: Add commands subparser to the repl.
            commands_help: The help of the commands group.
            commands_title: The title of the commands group.
            commands_description: The description of the commands group.
            exit_on_error: Set as false by default so it does not exit the
                repl if not explicitly wanted.
        """
        super().__init__(
            *args, **kwargs,
            add_help=False,
            exit_on_error=exit_on_error,
            formatter_class=REPLHelpFormater
        )

        # help text updated to match REPL ambient, not CLI
        if add_help is True:
            self.add_argument(
                "-h", "--help",
                action="help",
                default=argparse.SUPPRESS,
                help="show this help message."
            )

        # so commands does not have commands too
        if add_commands:
            if commands_title is None:
                commands_title: str = f"{self.prog} commands"

            self.commands = self.add_subparsers(
                title=commands_title,
                help=commands_help,
                description=commands_description
            )

    def add_command(
        self,
        action: Callable,
        name: str | None = None,
        help_txt: str | None = None
    ) -> Self:
        """
        Adds a command (subparser) to the REPL.

        Args:
            action (Callable): the function to be executed when the command
            is called.

            name (str, optional): The command name. Defaults to action
            function docstring.

            help_txt (str, optional): The help text. Defaults to action docstring.

        Returns:
            REPLParser: A command parser instance
        """
        if name is None:
            name = action.__name__
        if help_txt is None:
            help_txt = action.__doc__

        command_parser = self.commands.add_parser(
            name=name,
            description=help_txt,
            help=help_txt,
            add_commands=False
        )
        command_parser.set_defaults(func=action)
 
        return command_parser

    def parse_args(self, args=None, namespace=None) -> argparse.Namespace:
        """
        Parse given args.
        Raises a uniform exception whenever the parser attempts to exit.
        """
        try:
            return super().parse_args(args, namespace)

        except argparse.ArgumentError as e:
            logger.error(e)
            raise AttemptToExitError

        except SystemExit:  # because action= "help" exits on force
            raise AttemptToExitError

    # decorators for quick action setting.
    def add_cmd(self, *aliases: str, help_txt: str | None = None) -> Callable:
        """
        Decorator for adding a command with n aliases into the parser.
        Returns the last command_parser made.
        """
        def wrapper(action: Callable) -> set[Self]:
            command_names: tuple[str, ...]
            command_names = aliases if aliases else (action.__name__)
            command_help: str = help_txt or action.__doc__

            # each alias have it's own parser
            command_parsers: set[Self] = set()
            for command_name in command_names:
                command_parser: Self = self.add_command(
                    action, command_name, command_help
                )
                command_parsers.add(command_parser)

            return command_parsers
        return wrapper

    @staticmethod
    def add_args(*args, **kwargs) -> Callable:
        """Decorator for adding arguments to the newly made command."""
        def wrapper(command_parsers: set[Self]) -> Self:
            for command_parser in command_parsers:
                command_parser.add_argument(*args, **kwargs)
            return command_parsers
        return wrapper


def parse_and_execute(
    widget,
    line: str,
    suppress_attempt_to_exit: bool = False
) -> None:
    """Parse line and execute its action."""
    try:
        parsed: argparse.Namespace = widget.parser.parse_args(lexer(line))
    except AttemptToExitError as e:
        if suppress_attempt_to_exit:
            return
        raise AttemptToExitError from e

    func: Callable = getattr(parsed, "func", None)
    if func:
        func(widget, parsed)
