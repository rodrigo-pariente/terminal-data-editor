"""Module for having consistent error messages in the project applications."""

from collections.abc import Callable
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

error_msg = {}

def add_error_msg(error_name: str) -> Callable:
    """Add error associated functions to error_msg dictionary."""
    def wrapper(func: Callable) -> str:
        error_msg[error_name] = func()
    return wrapper

def perror(error_name: str, **kwargs) -> None:
    """Print error message along with possible extra arguments."""
    message = error_msg.get(error_name, "Unknown error: {}")
    formated_message = message.format(**kwargs)
    logger.error(formated_message)

# file_actions.py related:
@add_error_msg("DirectoryAlreadyExists")
def directory_already_exists() -> str:
    """Error for when file already exists."""
    return "ERROR: Directory {dirname} already exists."

@add_error_msg("DestinationMustBeDirectory")
def destination_must_be_directory() -> str:
    """Error for when given destination of a file isn't a valid directory."""
    return 'ERROR: Destination "{dirname}" must be directory.'

@add_error_msg("DirectoryNotFound")
def directory_not_found() -> str:
    """Error for when a directory is not found or does not exists."""
    return "ERROR: Directory {dirname} not found."

@add_error_msg("DirectoryOrFileNotFound")
def file_or_directory_not_found() -> str:
    """
    Error for when file or directory (not defined)
    is not found or does not exists.
    """
    return 'Could not find file/directory "{filename}".'

@add_error_msg("FileAlreadyExists")
def file_already_exists() -> str:
    """Error for when file already exists."""
    return "ERROR: File {filename} already exists."

@add_error_msg("PermissionDenied")
def permission_denied() -> str:
    """Error for when code is blocked by lack of system permissions."""
    permission_denied_msg = """
            ERROR: Permision denied. Try running this application 
            with adm powers.
            """
    return permission_denied_msg

# file_utils.py related:
@add_error_msg("UnsupportedFormat")
def unsupported_format() -> str:
    """Error for when trying to use unsupported format in file related functions"""
    msg = "{format} format is unsupported yet. Supported formats: {supported}"
    return msg

@add_error_msg("FileNotFound")
def file_not_found() -> str:
    """Error for when a directory is not found or does not exists."""
    return "ERROR: File {filename} not found."
