"""NAVIGATOR MANAGER"""

from actions.common_actions import common_commands
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator


class NavigatorManager:
    """Object for organizing and integrating navigator widgets."""
    def __init__(self,
                data_navigators: list[DataNavigator],
                file_navigators: list[FileNavigator]) -> None:
        self.data_navigators = data_navigators
        self.file_navigators = file_navigators
        self.commands = common_commands

        self.active_widget: DataNavigator | FileNavigator | None

        for data_navigator in self.data_navigators:
            if data_navigator.filename is not None:
                self.active_widget = data_navigator
                break

        if not hasattr(self, "active_widget"):
            if self.file_navigators:
                self.active_widget: FileNavigator = self.file_navigators[0]
            else:
                self.active_widget: None = None

    def automatic_refocus(self) -> None:
        """For refocusing in the apropriate widget."""
        widget_exists_1: bool = self.active_widget in self.data_navigators
        widget_exists_2: bool = self.active_widget in self.file_navigators
        if widget_exists_1 or widget_exists_2:
            return

        for navigators in (self.data_navigators, self.file_navigators):
            if navigators:
                self.active_widget = navigators[-1]
                return

        self.active_widget = None

    def run(self) -> None:
        """Execute the REPL ambient"""
        while True: # break if not command
            command, *args = input(">>>").strip().split()

            match command.lower():
                case _ if self.active_widget is not None and command in self.active_widget.commands:
                    self.active_widget.commands[command](self.active_widget, args)

                case _ if command in self.commands:
                    self.commands[command](self, args)

                case _:
                    print("ERROR: Invalid command.")
