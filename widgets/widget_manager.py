"""NAVIGATOR MANAGER"""


from actions.common_actions import common_commands
from widgets.data_navigator import DataNavigator
from widgets.file_navigator import FileNavigator
from parsing import command_parser


class WidgetManager:
    """Object for organizing and integrating navigator widgets."""
    def __init__(self,
                data_navigators: list[DataNavigator],
                file_navigator: FileNavigator) -> None:
        self.data_navigators = data_navigators
        self.file_navigator = file_navigator
        self.commands = common_commands

        self.active_widget: DataNavigator | FileNavigator

        for data_navigator in self.data_navigators:
            if data_navigator.filename is not None:
                self.active_widget = data_navigator
                break

        if not hasattr(self, "active_widget"):
            self.active_widget: FileNavigator = self.file_navigator

    def run(self) -> None:
        """Execute the REPL ambient"""
        while True:
            command, *args = command_parser(input(">>>"))
            match command.lower():
                case _ if command in self.active_widget.commands:
                    self.active_widget.commands[command](self.active_widget, args)

                case _ if command in self.commands:
                    self.commands[command](self, args)

                case _:
                    print("ERROR: Invalid command.")
