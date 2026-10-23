from datetime import UTC, datetime

jobs: dict[str, dict] = {}
documents: dict[str, dict] = {}

def utc_now() -> str:
    return datetime.now(UTC).isoformat()

def update_job(job_id: str, **changes: object) -> None:
    jobs[job_id].update(changes)
