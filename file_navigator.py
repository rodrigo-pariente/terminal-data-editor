from pathlib import Path
import sys
from typing import Any
from file_actions import commands


class FileNavigator:
    """Terminal file navigator"""
    def __init__(self, path: Path = Path(Path.cwd().anchor)) -> None:
        self.path = path
        self.commands: dict = commands

    def run(self) -> None:
        """Run file navigator REPL ambient"""
        while True:
            command, *args = input(">>>").strip().split()

            if command in self.commands:
                self.commands[command](self, args)
            else:
                print("ERROR: Invalid command.")


def main() -> None:
    """Main program execution"""
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(Path.cwd().anchor)

    fn = FileNavigator(path)

    fn.run()


if __name__ == "__main__":
    main()
