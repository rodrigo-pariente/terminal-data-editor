"""FILE NAVIGATOR"""

import dataclasses
from pathlib import Path
from actions.file_actions import file_commands


@dataclasses.dataclass
class FileNavigator:
    """Terminal file navigator for exploring files."""
    path: Path = Path(Path.cwd())
    commands: dict = dataclasses.field(
        default_factory=lambda: file_commands.copy()
    )
