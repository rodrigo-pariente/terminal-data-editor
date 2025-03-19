"""Module for storing error messages."""

from collections.abc import Callable
import json
from pathlib import Path
import logging


# GLOBAL LOGGING CONFIGURATION
logging.basicConfig(level=logging.DEBUG)
# add handler for debugging messages
logger = logging.getLogger(__name__)


error_messages_filepath: Path = (Path.cwd() / "messages/errors_en_US.json").resolve()
# TO-DO: change name to error_messages
with open(error_messages_filepath, "r", encoding="utf8") as file:
    error_msg = json.load(file)

def change_language(language: str) -> None:
    global error_msg

    error_messages_filepath: Path = (
        Path.cwd() / f"messages/errors_{language}.json"
    ).resolve()
    with open(error_messages_filepath, "r", encoding="utf8") as file:
        new_errors = json.load(file)
    error_msg.update(new_errors)

def get_error_message(error_name: str, **kwargs) -> str:
    """Get error message based on its name and kwargs"""
    message = error_msg.get(error_name, f"{error_name} - Unknown error.")
    try:
        formatted_message = message.format(**kwargs)
    except KeyError as e:
        formatted_message = f"{message} (Missing key: {e})"
    return formatted_message