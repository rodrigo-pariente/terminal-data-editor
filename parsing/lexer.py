""" Custom parsing methods. """

import shlex
from typing import Any

from parsing.safe_functions import SAFE_FUNCTIONS


def lexer(line: str, boxes: dict | None = None) -> list[str]:
    """
    Custom lexer for proper tokenizing Python data types,
    shell filenames with spaces.
    """
    tokens: list[str] = shlex.split(line, posix=False)

    if boxes is None:
        boxes: dict[str, str] = {"(": ")", "{": "}", "[": "]"}

    lexed: list[str] = []
    buffer: list[str] = []
    stack: list[str] = []
    for token in tokens:
        if stack:
            buffer.append(token)
            if token.endswith(boxes[stack[-1]]):
                stack.pop()
                if not stack:
                    lexed.append(" ".join(buffer))
                    buffer.clear()
        else:
            if token[0] in boxes and not token.endswith(boxes[token[0]]):
                stack.append(token[0])
                buffer.append(token)
            else:
                lexed.append(token)
    if buffer:
        lexed.append(" ".join(buffer))

    return lexed

def pre_parser(line: str, magick: bool = True) -> list[str]:
    """
    pre-parser for evaluating and execution of Python expressions 
    from within the REPL with the $python_command$ notation.

    Example of parsing:

    - `pre_parser("change -i 'file name.txt' -p age -s $str(10 + 2**3)$")`
      ['change', '-i', 'file name.txt', '-p', 'age', '-s', '18']
    """
    boxes: dict[str, str] = {"(": ")", "{": "}", "[": "]"}

    if magick:
        boxes.update({"$": "$"})
        # boxes.update({"\"": "\"", "'": "'"})
    lexed: list[str] = lexer(line, boxes)

    # parsed = [x if x.strip('\'"').isdigit() else x.strip('\'"') for x in lexed]
    # parsed = lexed
    parsed: list[str] = [x.strip("\"'") for x in lexed]

    # magick: evaluate python expressions in between $
    if not magick:
        return parsed

    parsed_magick = []
    for token in parsed:
        if not isinstance(token, str):
            continue

        if token.startswith("$*") and token.endswith("$"):
            tokens: Any = eval(token[2:-1])
            parsed_magick.extend(tokens)
            continue

        if token.startswith("$") and token.endswith("$"):
            token: Any = eval(token.strip("$")) 
        parsed_magick.append(str(token))

    return parsed_magick
