"""Module for storing custom parsing"""

import argparse
import shlex


class FunctionArgumentParser(argparse.ArgumentParser):
    """ArgumentParser for functions."""
    def __init__(self, func: str, description: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.func = func
        self.description = description
        self.prog = self.func
        self.exit_on_error = False

    def safe_parse_args(self, args) -> argparse.Namespace:
        """Parse given args. Protected from exiting application if ArgumentError raised."""
        try:
            parsed = self.parse_args(args)
            return parsed
        except argparse.ArgumentError as e:
            self.print_usage()
            raise e


def command_parser(usr_input: str) -> list[str]:
    """Custom parser for the project interests."""
    tokens: list[str] = shlex.split(usr_input, posix=False)

    boxes: dict[str, str] = {"(": ")", "{": "}", "[": "]"}

    parsed: list[str] = []
    buffer: list[str] = []
    open_char: None | str = None
    for token in tokens:
        if open_char:
            buffer.append(token)
            if token[-1].endswith(boxes[open_char]):
                parsed.append(" ".join(buffer))
                buffer = []
                open_char = None
        else:
            if token[0] in boxes and not token.endswith(boxes[token[0]]):
                open_char = token[0]
                buffer.append(token)
            else:
                parsed.append(token)
    if buffer:
        parsed.append(" ".join(buffer))

    return parsed
