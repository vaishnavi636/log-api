# Log API (FastAPI)

A REST API to read, filter, and analyze tab-separated log files from a directory.

## Log format
Each log entry is a single line with 4 tab-separated fields:

`Timestamp\tLevel\tComponent\tMessage`

Example:
```
Timestamp	Level	Component	Message
2025-05-07 10:00:00	INFO	UserAuth	User 'john.doe' logged in successfully.
2025-05-07 10:00:15	WARNING	GeoIP	Could not resolve IP address '192.168.1.100'.
2025-05-07 10:00:20	ERROR	Payment	Transaction failed for user 'jane.doe'.
2025-05-07 10:00:25	INFO	UserAuth	User 'alice.smith' logged out.
```

Assumptions:

Input format: One log entry per line with exactly 4 tab-separated fields:
timestamp, level, component, message.

Message may contain tabs: parsing uses split("\t", 3) so extra tabs are preserved in the message.

Timestamp formats supported:

YYYY-MM-DD HH:MM:SS (as shown in the prompt)

YYYY-MM-DDTHH:MM:SS (ISO-like convenience)

Timezone: timestamps are treated as naive/local time (no timezone conversion).

Header row: if a line equals Timestamp\tLevel\tComponent\tMessage, it is ignored.

Invalid lines: empty lines and header lines are ignored; malformed lines are skipped and counted as invalid_lines.

log_id generation: deterministic SHA1 of source_file:line_number:raw_line to keep IDs stable unless file content changes.

File selection: reads *.log files from LOG_DIR (default sample_logs/).

Ordering: entries are returned in deterministic order (by filename, then line order).

Pagination: /logs supports limit and offset (default limit=100, max limit=1000).

Endpoints

GET /logs

Query parameters (optional):

level (e.g. ERROR)

component (e.g. UserAuth)

start_time (e.g. 2025-05-07 10:00:10)

end_time (e.g. 2025-05-07 10:00:25)

limit (default 100)

offset (default 0)

GET /logs/stats

Returns:

total number of entries

counts per level

counts per component

GET /logs/{log_id}

Returns a specific log entry by deterministic log_id

GET /health


Run locally (Windows CMD)
1) Create venv and install dependencies

`py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt`

2) Run the API

`py -m uvicorn app.main:app --reload`


Open Swagger UI:

http://127.0.0.1:8000/docs

Configuration

Environment variables:

LOG_DIR (default: sample_logs)

DEFAULT_LIMIT (default: 100)

MAX_LIMIT (default: 1000)

LOG_FILE_GLOB (default: *.log)

Example:

set LOG_DIR=sample_logs
**py -m uvicorn app.main:app --reload**

Example requests

All logs:

GET http://127.0.0.1:8000/logs

Filter by level:

GET http://127.0.0.1:8000/logs?level=ERROR

Filter by component:

GET http://127.0.0.1:8000/logs?component=UserAuth

Filter by time (space format; URL-encoded space as %20):

GET http://127.0.0.1:8000/logs?start_time=2025-05-07%2010:00:10&end_time=2025-05-07%2010:00:25

Stats:

GET http://127.0.0.1:8000/logs/stats


Testing

Run tests with:

`pytest -q`
