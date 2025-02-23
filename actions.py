from collections.abc import Callable
from path_utils import *
from file_utils import *
import sys

#dn: DataNavigator
commands = {}

def add_command(command: str) -> Callable:
    """Decorator to add new commands automaticaly to commands dictionary."""
    def wrapper(func):
        commands[command] = func
        return func
    return wrapper

@add_command("..")
def back(dn) -> None:
    """Takes DataNavigator path a step back."""
    if dn.path:
        dn.path = path_pop(dn.path)
    else:
        print("ERROR: You are at root level.")

@add_command("\\")
def do_nothing(*args) -> None:
    """This function does nothing."""
    pass

@add_command("\\exit")
def exit(*args) -> None:
    """Exit the script."""
    sys.exit(0) # wanted to be break

@add_command("\\+l")
def literal_on(dn) -> None:
    """Turn DataNavigator literal flag ON."""
    dn.literal = True

@add_command("\\-l")
def literal_off(dn) -> None:
    """Turn DataNavigator literal flag OFF."""
    dn.literal = False

@add_command("\\restart")
def restart(dn) -> None:
    """Restart DataNavigator data to the original state."""
    dn.data = dn.secure_data

@add_command("\\save")
def save(dn) -> None:
    """Save DataNavigator modified data into filename."""
    save_json(dn.filename, dn.data)
    print(f"Saved at {dn.filename}.")
