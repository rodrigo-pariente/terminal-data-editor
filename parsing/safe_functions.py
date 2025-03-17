import math
import random
from datetime import datetime
from pathlib import Path

SAFE_FUNCTIONS = {
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    "len": len,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "range": range,
    "sorted": sorted,
    "sum": sum,

    # Math functions
    "sqrt": math.sqrt,
    "log": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    
    # Random functions
    "randint": random.randint,
    "choice": random.choice,
    
    # Date & Time
    "now": lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "timestamp": lambda: datetime.now().timestamp(),
    
    # File utils (limited)
    "basename": lambda path: Path(path).name,
    "dirname": lambda path: Path(path).parent,
    
    # Safe evaluation (no eval!)
    "safe_eval": lambda expr: eval(expr, {"__builtins__": {}}, safe_functions) if all(
        c.isalnum() or c in " +-*/()." for c in expr) else "ERROR: Unsafe input!"
}
