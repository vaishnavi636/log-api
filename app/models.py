from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List


class LogEntry(BaseModel):
    log_id: str = Field(..., description="Deterministic unique ID for this log entry")
    timestamp: datetime
    level: str
    component: str
    message: str
    source_file: str
    line_number: int


class LogsResponse(BaseModel):
    total_matched: int
    limit: int
    offset: int
    items: List[LogEntry]


class StatsResponse(BaseModel):
    total_entries: int
    invalid_lines: int
    by_level: Dict[str, int]
    by_component: Dict[str, int]
