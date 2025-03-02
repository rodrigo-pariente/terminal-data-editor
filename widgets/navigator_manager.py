"""NAVIGATOR MANAGER"""

from actions.common_actions import common_commands
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator


class NavigatorManager:
    """Object for organizing and integrating navigator widgets."""
    def __init__(self,
                data_navigator: DataNavigator,
                file_navigator: FileNavigator) -> None:
        self.data_navigator = data_navigator
        self.file_navigator = file_navigator
        self.commands = common_commands

        self.active_navigator: DataNavigator | FileNavigator
        if self.data_navigator.filename is None:
            self.active_navigator = self.file_navigator
        else:
            self.active_navigator = self.data_navigator

    def run(self) -> None:
        """Execute the REPL ambient"""
        while True:
            command, *args = input(">>>").strip().split()

            match command.lower():
                case _ if command in self.active_navigator.commands:
                    self.active_navigator.commands[command](self.active_navigator, args)

                case _ if command in self.commands:
                    self.commands[command](self, args)

                case "explorer" if not args:
                    self.active_navigator = self.file_navigator

                case "editor" if not args:
                    self.active_navigator = self.data_navigator

                case _:
                    print("ERROR: Invalid command.")
