"""NAVIGATOR MANAGER"""

from actions.common_actions import common_commands
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator


class NavigatorManager:
    """Object for organizing and integrating navigator widgets."""
    def __init__(self,
                data_navigators: list[DataNavigator],
                file_navigator: FileNavigator) -> None:
        self.data_navigators = data_navigators
        self.file_navigator = file_navigator
        self.commands = common_commands

        self.active_navigator: DataNavigator | FileNavigator

        for data_navigator in self.data_navigators:
            if data_navigator.filename is not None:
                self.active_navigator = data_navigator
                break

        if not hasattr(self, "active_navigator"):
            self.active_navigator = self.file_navigator

    def run(self) -> None:
        """Execute the REPL ambient"""
        while True:
            command, *args = input(">>>").strip().split()

            match command.lower():
                case _ if command in self.active_navigator.commands:
                    self.active_navigator.commands[command](self.active_navigator, args)

                case _ if command in self.commands:
                    self.commands[command](self, args)

                case _:
                    print("ERROR: Invalid command.")
