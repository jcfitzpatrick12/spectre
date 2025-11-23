"""Job management service for async recording operations."""

import datetime
import enum
import json
import os
import pathlib
import subprocess
import uuid
from typing import Any, Optional

import spectre_core.config


class JobStatus(enum.Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    """Represents a recording job with persistent state."""

    def __init__(
        self,
        job_id: str,
        tag: str,
        duration: int,
        start_time: str,
        status: str = JobStatus.PENDING.value,
        progress: float = 0.0,
        error: Optional[str] = None,
        result_path: Optional[str] = None,
        pid: Optional[int] = None,
    ):
        self.job_id = job_id
        self.tag = tag
        self.duration = duration
        self.start_time = start_time
        self.status = status
        self.progress = progress
        self.error = error
        self.result_path = result_path
        self.pid = pid

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "tag": self.tag,
            "duration": self.duration,
            "start_time": self.start_time,
            "status": self.status,
            "progress": self.progress,
            "error": self.error,
            "result_path": self.result_path,
            "pid": self.pid,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        """Create job instance from dictionary."""
        return cls(
            job_id=data["job_id"],
            tag=data["tag"],
            duration=data["duration"],
            start_time=data["start_time"],
            status=data.get("status", JobStatus.PENDING.value),
            progress=data.get("progress", 0.0),
            error=data.get("error"),
            result_path=data.get("result_path"),
            pid=data.get("pid"),
        )


def _get_jobs_dir() -> pathlib.Path:
    """Get the directory where job state files are stored."""
    # Use spectre-core config to get base data directory
    base_dir = pathlib.Path(spectre_core.config.paths.get_spectre_data_dir_path())
    jobs_dir = base_dir / "jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    return jobs_dir


def _get_job_file_path(job_id: str) -> pathlib.Path:
    """Get the file path for a specific job's state."""
    return _get_jobs_dir() / f"{job_id}.json"


def create_job(tag: str, duration: int) -> Job:
    """Create a new job with a unique ID and save it to disk.

    Args:
        tag: The receiver configuration tag
        duration: Recording duration in seconds

    Returns:
        The created Job instance
    """
    job_id = str(uuid.uuid4())
    start_time = datetime.datetime.utcnow().isoformat()

    job = Job(
        job_id=job_id,
        tag=tag,
        duration=duration,
        start_time=start_time,
        status=JobStatus.PENDING.value,
    )

    _save_job(job)
    return job


def get_job(job_id: str) -> Optional[Job]:
    """Retrieve a job by ID from disk.

    Args:
        job_id: The unique job identifier

    Returns:
        Job instance if found, None otherwise
    """
    job_file = _get_job_file_path(job_id)

    if not job_file.exists():
        return None

    try:
        with open(job_file, 'r') as f:
            data = json.load(f)
        return Job.from_dict(data)
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def update_job(
    job_id: str,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    error: Optional[str] = None,
    result_path: Optional[str] = None,
    pid: Optional[int] = None,
) -> bool:
    """Update job state and save to disk.

    Args:
        job_id: The unique job identifier
        status: New status (if provided)
        progress: New progress percentage 0-100 (if provided)
        error: Error message (if provided)
        result_path: Path to result file (if provided)
        pid: Process ID (if provided)

    Returns:
        True if update succeeded, False if job not found
    """
    job = get_job(job_id)
    if not job:
        return False

    if status is not None:
        job.status = status
    if progress is not None:
        job.progress = progress
    if error is not None:
        job.error = error
    if result_path is not None:
        job.result_path = result_path
    if pid is not None:
        job.pid = pid

    _save_job(job)
    return True


def list_jobs(limit: Optional[int] = None) -> list[Job]:
    """List all jobs, sorted by start time (newest first).

    Args:
        limit: Maximum number of jobs to return (optional)

    Returns:
        List of Job instances
    """
    jobs_dir = _get_jobs_dir()
    jobs = []

    for job_file in jobs_dir.glob("*.json"):
        try:
            with open(job_file, 'r') as f:
                data = json.load(f)
            jobs.append(Job.from_dict(data))
        except (json.JSONDecodeError, KeyError, OSError):
            continue

    # Sort by start time, newest first
    jobs.sort(key=lambda j: j.start_time, reverse=True)

    if limit:
        jobs = jobs[:limit]

    return jobs


def delete_job(job_id: str) -> bool:
    """Delete a job from disk.

    Args:
        job_id: The unique job identifier

    Returns:
        True if deletion succeeded, False if job not found
    """
    job_file = _get_job_file_path(job_id)

    if not job_file.exists():
        return False

    try:
        job_file.unlink()
        return True
    except OSError:
        return False


def cancel_job(job_id: str) -> bool:
    """Cancel a running job by killing its process.

    Args:
        job_id: The unique job identifier

    Returns:
        True if cancellation succeeded, False otherwise
    """
    job = get_job(job_id)
    if not job:
        return False

    # Can only cancel pending or running jobs
    if job.status not in [JobStatus.PENDING.value, JobStatus.RUNNING.value]:
        return False

    # Kill the process if it exists
    if job.pid:
        try:
            os.kill(job.pid, 15)  # SIGTERM
        except ProcessLookupError:
            # Process already dead
            pass
        except PermissionError:
            # Can't kill process (shouldn't happen in same container)
            pass

    # Update status to cancelled
    update_job(job_id, status=JobStatus.CANCELLED.value)
    return True


def calculate_progress(job: Job) -> float:
    """Calculate job progress based on elapsed time.

    Args:
        job: The Job instance

    Returns:
        Progress percentage (0-100)
    """
    if job.status == JobStatus.COMPLETED.value:
        return 100.0

    if job.status in [JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
        return job.progress  # Return last known progress

    # Calculate based on elapsed time
    start = datetime.datetime.fromisoformat(job.start_time)
    elapsed = (datetime.datetime.utcnow() - start).total_seconds()

    if elapsed >= job.duration:
        return 100.0

    progress = (elapsed / job.duration) * 100
    return min(progress, 100.0)


def is_process_running(pid: Optional[int]) -> bool:
    """Check if a process is still running.

    Args:
        pid: Process ID to check

    Returns:
        True if process is running, False otherwise
    """
    if not pid:
        return False

    try:
        # Send signal 0 to check if process exists
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it
        return True


def _save_job(job: Job) -> None:
    """Save job state to disk (internal helper)."""
    job_file = _get_job_file_path(job.job_id)

    with open(job_file, 'w') as f:
        json.dump(job.to_dict(), f, indent=2)
