from collections.abc import Callable
from data_navigator import DataNavigator
from path_utils import path_pop
from file_utils import save_json
import sys

def exit(*args) -> None:
    sys.exit(0) # wanted to be break

def restart(dn: DataNavigator) -> None:
    dn.data = dn.secure_data

def save(dn: DataNavigator) -> None:
    save_json(dn.filename, dn.data)
    print(f"Saved at {dn.filename}.")

def switch_literal(flag: str) -> Callable:
    def func(dn: DataNavigator):
        if flag == "on":
            dn.literal = True
        else:
            dn.literal = False

        print(f"Literal flag turned {flag}.")
    return func

def do_nothing(*args) -> None:
    pass

def back(dn: DataNavigator) -> None:
    if dn.path:
        dn.path = path_pop(dn.path)
    else:
        print("ERROR: You are at root level.")


actions = {
    "\\exit": exit,
    "\\restart": restart,
    "\\save": save,
    "\\-l": switch_literal("off"),
    "\\+l": switch_literal("on"),
    "\\": do_nothing,
    "..": back,
}

