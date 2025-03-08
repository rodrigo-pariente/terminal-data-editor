"""Module for storing custom parsing methods."""

import argparse
import shlex
from typing import Any


class FunctionArgumentParser(argparse.ArgumentParser):
    """ArgumentParser for the custom REPL commands."""
    def __init__(self, func: str, description: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.func = func
        self.description = description
        self.prog = self.func
        self.exit_on_error = False

    def safe_parse_args(self, args) -> argparse.Namespace:
        """
        Parse given args.
        Protected from exiting application if ArgumentError raised.
        """
        try:
            parsed = self.parse_args(args)
            return parsed
        except argparse.ArgumentError as e:
            self.print_usage()
            raise e


def command_parser(usr_input: str) -> list[str]:
    """
    Custom parser for proper tokenizing Python data types, 
    shell filenames with spaces, and execution of Python expressions
    from within the REPL with the $python_command$ notation.

    Example of parsing:

    - `command_parser("change -i 'file name.txt' -p age -s $str(10 + 2**3)$")`
      ['change', '-i', 'file name.txt', '-p', 'age', '-s', '18']

    """
    tokens: list[str] = shlex.split(usr_input, posix=False)

    boxes: dict[str, str] = {"(": ")", "{": "}", "[": "]", "$": "$"}

    parsed: list[str] = []
    buffer: list[str] = []
    stack: list[str] = []
    for token in tokens:
        if stack:
            buffer.append(token)
            if token.endswith(boxes[stack[-1]]):
                stack.pop()
                if not stack:
                    parsed.append(" ".join(buffer))
                    buffer.clear()
        else:
            if token[0] in boxes and not token.endswith(boxes[token[0]]):
                stack.append(token[0])
                buffer.append(token)
            else:
                parsed.append(token)
    if buffer:
        parsed.append(" ".join(buffer))

    parsed = [x.strip('\'"') for x in parsed]

    parsed_magick = []
    for token in parsed:
        if token.startswith("$*") and token.endswith("$"):
            tokens: Any = eval(token[2:-1])
            parsed_magick.extend(tokens)
            continue

        if token.startswith("$") and token.endswith("$"):
            token: Any = eval(token.strip("$")) # add safe_functions
        parsed_magick.append(token)

    return parsed_magick

