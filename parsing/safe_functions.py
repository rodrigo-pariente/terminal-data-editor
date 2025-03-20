"""Safe functions for magick parsing."""

import math
import random
from datetime import datetime
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


user_vars: dict[str, Any] = {}

def add_vars(**kwargs) -> None:
    """Add user's vars to a safe scope."""
    user_vars.update(kwargs)
    print(user_vars)

def get_vars() -> dict[str, Any]:
    """Return the user_vars dict."""
    return user_vars.copy()

def safe_evaluation(code: str) -> Any:
    """Safe evaluation of pythonic expressions."""
    # adding vars
    tokens: list[str] = code.strip().split()
    if len(tokens) >= 3 and tokens[1] == "=" and tokens.count("=") == 1:
        add_vars(**{tokens[0]: safe_evaluation(" ".join(tokens[2:]))})

        # pass a commentary command so argparse does not warn invalid command
        return "#"

    # evaluating expressions
    try:
        return eval(
            code, 
            {"__builtins__": {}}, 
            SAFE_FUNCTIONS | user_vars
        )
    except Exception as e:
        logger.error(f"Syntax error when evaluating: {e}")
        return "#"

SAFE_FUNCTIONS = {
    "int": int, "float": float, "str": str,
    "list": list, "tuple": tuple, "dict": dict, "set": set,

    "len": len, "abs": abs, "round": round, 
    "min": min, "max": max, "sum": sum, "sorted": sorted,
    "range": range, "map": map, "filter": filter, "zip": zip,

    "sqrt": math.sqrt, "log": math.log, 
    "sin": math.sin, "cos": math.cos, "tan": math.tan,

    "randint": random.randint, "choice": random.choice,

    "now": lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "timestamp": lambda: datetime.now().timestamp(),

    "basename": lambda path: Path(path).name,
    "dirname": lambda path: str(Path(path).parent),

    "add": add_vars,
    "vars": get_vars,
}
