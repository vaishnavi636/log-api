from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
from typing import Iterator, Optional, Tuple


HEADER = "Timestamp\tLevel\tComponent\tMessage"


@dataclass(frozen=True)
class ParseResult:
    ok: bool
    entry: Optional[dict] = None
    error: Optional[str] = None


def parse_timestamp(value: str) -> datetime:
    """
    Supported formats:
      - 'YYYY-MM-DD HH:MM:SS'
      - 'YYYY-MM-DDTHH:MM:SS'  (ISO-ish convenience)
    """
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid timestamp format: {value!r}")


def make_log_id(source_file: str, line_number: int, raw_line: str) -> str:
    """
    Deterministic ID so it stays stable across runs unless the file content changes.
    """
    payload = f"{source_file}:{line_number}:{raw_line}".encode("utf-8", errors="replace")
    return hashlib.sha1(payload).hexdigest()


def parse_line(raw_line: str, source_file: str, line_number: int) -> ParseResult:
    line = raw_line.rstrip("\n")

    # Skip empty lines
    if not line.strip():
        return ParseResult(ok=False, error="empty")

    # Skip header line (exact match or trimmed)
    if line.strip() == HEADER:
        return ParseResult(ok=False, error="header")

    # Safe split: message can contain tabs -> maxsplit=3
    parts = line.split("\t", 3)
    if len(parts) != 4:
        return ParseResult(ok=False, error="bad_columns")

    ts_s, level, component, message = (p.strip() for p in parts)
    try:
        ts = parse_timestamp(ts_s)
    except ValueError as e:
        return ParseResult(ok=False, error=str(e))

    log_id = make_log_id(source_file=source_file, line_number=line_number, raw_line=line)

    entry = {
        "log_id": log_id,
        "timestamp": ts,
        "level": level,
        "component": component,
        "message": message,
        "source_file": source_file,
        "line_number": line_number,
    }
    return ParseResult(ok=True, entry=entry)


def iter_log_files(log_dir: Path, pattern: str) -> Iterator[Path]:
    # Yield files in deterministic order for predictability
    for path in sorted(log_dir.glob(pattern)):
        if path.is_file():
            yield path


def iter_logs_from_dir(log_dir: Path, pattern: str) -> Tuple[Iterator[dict], "StatsCounter"]:
    """
    Returns:
      - iterator of parsed log dicts
      - StatsCounter that tracks totals/invalid lines, updated as you iterate
    """
    counter = StatsCounter()

    def _gen() -> Iterator[dict]:
        for file_path in iter_log_files(log_dir, pattern):
            source_file = file_path.name
            try:
                with file_path.open("r", encoding="utf-8", errors="replace") as f:
                    for idx, raw_line in enumerate(f, start=1):
                        res = parse_line(raw_line, source_file, idx)
                        if not res.ok:
                            counter.invalid_lines += 1 if res.error not in ("empty", "header") else 0
                            continue
                        counter.total_entries += 1
                        level = res.entry["level"]
                        comp = res.entry["component"]
                        counter.by_level[level] = counter.by_level.get(level, 0) + 1
                        counter.by_component[comp] = counter.by_component.get(comp, 0) + 1
                        yield res.entry
            except FileNotFoundError:
                continue

    return _gen(), counter


class StatsCounter:
    def __init__(self) -> None:
        self.total_entries: int = 0
        self.invalid_lines: int = 0
        self.by_level: dict[str, int] = {}
        self.by_component: dict[str, int] = {}
