# ------------------------------
# Audit / log
# ------------------------------

from pathlib import Path
from auxiliary_functions import _now_str, _project_dir



class Audit:
    """Collects logs in memory and can print/export them to txt."""

    def __init__(self) -> None:
        self.log: list[str] = []

    def write_log(self, log_info: str) -> None:
        """Adds a log line with a timestamp."""
        self.log.append(f"[{_now_str()}] {log_info}")

    def print_log(self) -> None:
        """Prints the log to stdout."""
        for line in self.log:
            print(line)

    def export_log_txt(self, file_name: str = "log.txt") -> Path:
        """Saves log into file (append).

        Returns:
            Path to log file.
        """
        log_path = _project_dir() / file_name
        with log_path.open("a", encoding="utf-8") as f:
            for line in self.log:
                f.write(line if line.endswith("\n") else line + "\n")
        return log_path