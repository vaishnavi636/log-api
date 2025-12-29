from fastapi import FastAPI, HTTPException, Query

from .config import LOG_DIR, LOG_FILE_GLOB, DEFAULT_LIMIT
from .models import LogEntry, LogsResponse, StatsResponse
from .service import get_logs_page, get_log_by_id, get_stats
from .parser import parse_timestamp

app = FastAPI(title="Log API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Log API is running. Visit /docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/logs", response_model=LogsResponse)
def read_logs(
    level: str | None = None,
    component: str | None = None,
    start_time: str | None = Query(default=None, description="YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS"),
    end_time: str | None = Query(default=None, description="YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS"),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
):
    try:
        st = parse_timestamp(start_time) if start_time else None
        et = parse_timestamp(end_time) if end_time else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if st and et and st > et:
        raise HTTPException(status_code=400, detail="start_time must be <= end_time")
    try:
        total, items = get_logs_page(
            log_dir=LOG_DIR,
            pattern=LOG_FILE_GLOB,
            level=level,
            component=component,
            start_time=st,
            end_time=et,
            limit=limit,
            offset=offset,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"total_matched": total, "limit": limit, "offset": offset, "items": items}


@app.get("/logs/stats", response_model=StatsResponse)
def read_stats():
    data = get_stats(LOG_DIR, LOG_FILE_GLOB)
    return data


@app.get("/logs/{log_id}", response_model=LogEntry)
def read_log_by_id(log_id: str):
    entry = get_log_by_id(LOG_DIR, LOG_FILE_GLOB, log_id)
    if not entry:
        raise HTTPException(status_code=404, detail="log_id not found")
    return entry
