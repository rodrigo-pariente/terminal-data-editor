"""File Navigator widget module"""

import dataclasses
from pathlib import Path

from actions.file_actions import file_navigator_parser
from parsing.repl_parser import CommandParser


@dataclasses.dataclass
class FileNavigator:
    """Terminal file navigator for exploring files."""
    path: Path = Path(Path.cwd())
    parser: CommandParser = file_navigator_parser
