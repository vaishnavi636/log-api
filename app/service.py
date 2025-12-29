from __future__ import annotations

from datetime import datetime
from typing import Iterator, Optional, Tuple, Dict

from .config import DEFAULT_LIMIT, MAX_LIMIT
from .parser import iter_logs_from_dir


def validate_pagination(limit: int, offset: int) -> Tuple[int, int]:
    if limit <= 0:
        raise ValueError("limit must be > 0")
    if limit > MAX_LIMIT:
        raise ValueError(f"limit must be <= {MAX_LIMIT}")
    if offset < 0:
        raise ValueError("offset must be >= 0")
    return limit, offset


def apply_filters(
    logs: Iterator[dict],
    level: Optional[str],
    component: Optional[str],
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> Iterator[dict]:
    for entry in logs:
        if level and entry["level"] != level:
            continue
        if component and entry["component"] != component:
            continue
        if start_time and entry["timestamp"] < start_time:
            continue
        if end_time and entry["timestamp"] > end_time:
            continue
        yield entry


def get_logs_page(
    log_dir,
    pattern: str,
    level: Optional[str],
    component: Optional[str],
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> Tuple[int, list[dict]]:
    limit, offset = validate_pagination(limit, offset)

    logs_iter, _counter = iter_logs_from_dir(log_dir, pattern)
    filtered = apply_filters(logs_iter, level, component, start_time, end_time)

    total_matched = 0
    page: list[dict] = []

    start = offset
    end = offset + limit

    for entry in filtered:
        if total_matched >= start and total_matched < end:
            page.append(entry)
        total_matched += 1

    return total_matched, page


def get_log_by_id(log_dir, pattern: str, log_id: str) -> Optional[dict]:
    logs_iter, _counter = iter_logs_from_dir(log_dir, pattern)
    for entry in logs_iter:
        if entry["log_id"] == log_id:
            return entry
    return None


def get_stats(log_dir, pattern: str) -> Dict:
    logs_iter, counter = iter_logs_from_dir(log_dir, pattern)
    # Exhaust iterator to fill counter
    for _ in logs_iter:
        pass
    return {
        "total_entries": counter.total_entries,
        "invalid_lines": counter.invalid_lines,
        "by_level": counter.by_level,
        "by_component": counter.by_component,
    }
