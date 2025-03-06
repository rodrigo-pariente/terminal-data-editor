"""Module for storing custom parsing"""

import argparse


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
