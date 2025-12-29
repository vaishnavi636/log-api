from pathlib import Path
import os


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


LOG_DIR = Path(os.getenv("LOG_DIR", "sample_logs"))

DEFAULT_LIMIT = _to_int(os.getenv("DEFAULT_LIMIT", "100"), 100)
MAX_LIMIT = _to_int(os.getenv("MAX_LIMIT", "1000"), 1000)

# Which files to read (assumption: .log files only)
LOG_FILE_GLOB = os.getenv("LOG_FILE_GLOB", "*.log")
