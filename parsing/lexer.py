""" Custom lexer method. """

import re
import shlex
from typing import Any

from parsing.safe_functions import SAFE_FUNCTIONS


def lexer(usr_input: str) -> list[str]:
    """
    Custom lexer/pre-parser for proper tokenizing Python data types, 
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

    # magick: evaluate python expressions in between $
    parsed_magick = []
    for token in parsed:
        if token.startswith("$*") and token.endswith("$"):
            tokens: Any = safe_func(token[2:-1])
            parsed_magick.extend(tokens)
            continue

        if token.startswith("$") and token.endswith("$"):
            token: Any = safe_func(token.strip("$")) 
        parsed_magick.append(token)

    return parsed_magick
