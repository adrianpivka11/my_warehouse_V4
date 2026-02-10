"""
auxiliary functions used in different files of project

"""


from pathlib import Path
import datetime as dt


def _now_str() -> str:
    """Returns the current time in a readable format for log."""
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _project_dir() -> Path:
    """Returns the directory where this script is located."""
    return Path(__file__).resolve().parent

def _exports_dir() -> Path:
    """Returns the directory export (CSV/JSON/TXT)."""
    d = _project_dir() / "exports"
    d.mkdir(exist_ok=True)
    return d


def _read_int(prompt: str) -> int:
    """Reads an integer from input; repeats until successful."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Enter number.")


def _read_float(prompt: str) -> float:
    """Reads an float from input; repeats until successful."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Enter number (e.g. 12.50).")


def _read_bool(prompt: str) -> bool:
    """Reads a boolean from input. If user enters 'y/yes/1/true' -> True, otherwise False."""
    raw = input(prompt).strip().lower()
    return raw in {"y", "yes", "1", "true", "t"}