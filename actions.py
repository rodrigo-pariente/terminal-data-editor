from collections.abc import Callable
from path_utils import path_pop
from file_utils import save_json
import sys


commands = {}

def add_command(command: str) -> Callable:
    def wrapper(func):
        commands[command] = func
        return func
    return wrapper

@add_command("\\exit")
def exit(*args) -> None:
    sys.exit(0) # wanted to be break

@add_command("\\restart")
def restart(dn) -> None:
    dn.data = dn.secure_data

@add_command("\\save")
def save(dn) -> None:
    save_json(dn.filename, dn.data)
    print(f"Saved at {dn.filename}.")

@add_command("\\+l")
def literal_on(dn) -> None:
    dn.literal = True

@add_command("\\-l")
def literal_off(dn) -> None:
    dn.literal = False

@add_command("\\")
def do_nothing(*args) -> None:
    pass

@add_command("..")
def back(dn) -> None:
    if dn.path:
        dn.path = path_pop(dn.path)
    else:
        print("ERROR: You are at root level.")
