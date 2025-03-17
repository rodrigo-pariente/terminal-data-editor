"""Module for storing error messages."""

from collections.abc import Callable
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

error_msg: dict[str, str] = {}

def add_error_msg(error_name: str) -> Callable:
    """Decorator for adding new messages into the error_msg dictionary."""
    def wrapper(func: Callable) -> None:
        error_msg[error_name] = func()
    return wrapper

def perror(error_name: str, **kwargs) -> None:
    """Standard function for displaying error messages."""
    message = error_msg.get(error_name, f"ERROR: {error_name} - Unknown error.")
    try:
        formatted_message = message.format(**kwargs)
    except KeyError as e:
        formatted_message = f"{message} (Missing key: {e})"
    
    logger.error(formatted_message)

# file_actions.py related:
@add_error_msg("DirectoryAlreadyExists")
def directory_already_exists() -> str:
    """Error for when a directory already exists."""
    return "ERROR: Directory {dirname} already exists."

@add_error_msg("DestinationMustBeDirectory")
def destination_must_be_directory() -> str:
    """Error for when the destination of a file isn't a valid directory."""
    return 'ERROR: Destination "{dirname}" must be a directory.'

@add_error_msg("DirectoryNotFound")
def directory_not_found() -> str:
    """Error for when a directory is not found."""
    return "ERROR: Directory {dirname} not found."

@add_error_msg("DirectoryOrFileNotFound")
def file_or_directory_not_found() -> str:
    """Error for when a file or directory is not found."""
    return 'ERROR: Could not find file/directory "{filename}".'

@add_error_msg("FileAlreadyExists")
def file_already_exists() -> str:
    """Error for when a file already exists."""
    return "ERROR: File {filename} already exists."

@add_error_msg("PermissionDenied")
def permission_denied() -> str:
    """Error for when the code is blocked due to lack of system permissions."""
    return (
        "ERROR: Permission denied. Try running this application "
        "with administrator privileges."
    )

# file_utils.py related:
@add_error_msg("UnsupportedFormat")
def unsupported_format() -> str:
    """Error for when trying to use an unsupported format in file-related functions."""
    return "{format} format is unsupported. Supported formats: {supported}"

@add_error_msg("FileNotFound")
def file_not_found() -> str:
    """Error for when a file is not found."""
    return "ERROR: File {filename} not found."

# data_utils.py related:
@add_error_msg("InvalidIndex")
def invalid_index() -> str:
    """Error for when an invalid index is accessed."""
    return "ERROR: Index {index} in the given path does not exist in {data}."
