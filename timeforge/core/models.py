"""Data models for TimeForge.

This module defines the core data structures used throughout the application:
- TimeEntry: Represents a single time tracking record
- Project: Represents a project with metadata
- Session: Represents the current active tracking session
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class TimeEntry:
    """Represents a single time tracking record.

    Attributes:
        id: Unique identifier for the entry.
        project: Name of the project this entry belongs to.
        description: Optional description of the work done.
        start_time: When the time tracking started (ISO format string).
        end_time: When the time tracking ended (ISO format string), None if active.
        duration: Total duration in seconds (computed from start/end).
        paused_duration: Total time spent paused in seconds.
        tags: Optional list of tags for categorization.
        git_commits: Optional list of associated git commit hashes.
        created_at: When this entry was created (ISO format string).
        updated_at: When this entry was last modified (ISO format string).
    """

    def __init__(
        self,
        project: str,
        description: str = "",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        duration: float = 0.0,
        paused_duration: float = 0.0,
        tags: Optional[List[str]] = None,
        git_commits: Optional[List[str]] = None,
        entry_id: Optional[str] = None,
    ):
        """Initialize a TimeEntry instance.

        Args:
            project: Name of the project.
            description: Description of the work.
            start_time: ISO format start time string. Defaults to now.
            end_time: ISO format end time string. None if still running.
            duration: Pre-computed duration in seconds.
            paused_duration: Total paused time in seconds.
            tags: List of category tags.
            git_commits: List of associated git commit hashes.
            entry_id: Custom entry ID. Auto-generated if not provided.
        """
        self.id: str = entry_id or str(uuid.uuid4())[:8]
        self.project: str = project
        self.description: str = description
        self.start_time: str = start_time or datetime.now().isoformat()
        self.end_time: Optional[str] = end_time
        self.duration: float = duration
        self.paused_duration: float = paused_duration
        self.tags: List[str] = tags or []
        self.git_commits: List[str] = git_commits or []
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()

    @property
    def is_active(self) -> bool:
        """Check if this entry is currently being tracked (no end time)."""
        return self.end_time is None

    @property
    def start_datetime(self) -> datetime:
        """Get start time as a datetime object."""
        return datetime.fromisoformat(self.start_time)

    @property
    def end_datetime(self) -> Optional[datetime]:
        """Get end time as a datetime object, or None if still active."""
        if self.end_time is None:
            return None
        return datetime.fromisoformat(self.end_time)

    def compute_duration(self) -> float:
        """Compute the effective duration (total - paused) in seconds.

        If the entry is still active, computes duration from start to now.

        Returns:
            Effective duration in seconds.
        """
        if self.end_time:
            end = datetime.fromisoformat(self.end_time)
        else:
            end = datetime.now()
        start = datetime.fromisoformat(self.start_time)
        total = (end - start).total_seconds()
        return max(0.0, total - self.paused_duration)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the TimeEntry to a dictionary.

        Returns:
            Dictionary representation of this entry.
        """
        return {
            "id": self.id,
            "project": self.project,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "paused_duration": self.paused_duration,
            "tags": self.tags,
            "git_commits": self.git_commits,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeEntry":
        """Deserialize a TimeEntry from a dictionary.

        Args:
            data: Dictionary containing entry data.

        Returns:
            A new TimeEntry instance.
        """
        entry = cls(
            project=data["project"],
            description=data.get("description", ""),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            duration=data.get("duration", 0.0),
            paused_duration=data.get("paused_duration", 0.0),
            tags=data.get("tags", []),
            git_commits=data.get("git_commits", []),
            entry_id=data.get("id"),
        )
        entry.created_at = data.get("created_at", entry.created_at)
        entry.updated_at = data.get("updated_at", entry.updated_at)
        return entry

    def __repr__(self) -> str:
        """Return a string representation of the TimeEntry."""
        status = "active" if self.is_active else "completed"
        return (
            f"TimeEntry(id={self.id}, project='{self.project}', "
            f"status={status})"
        )


class Project:
    """Represents a project with aggregated metadata.

    Attributes:
        name: Unique name of the project.
        description: Optional project description.
        color: Display color for the project (ANSI color name).
        created_at: When the project was first created (ISO format string).
        total_time: Total tracked time in seconds across all entries.
        entry_count: Number of time entries for this project.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        color: str = "cyan",
        created_at: Optional[str] = None,
        total_time: float = 0.0,
        entry_count: int = 0,
    ):
        """Initialize a Project instance.

        Args:
            name: Unique project name.
            description: Project description.
            color: ANSI color name for terminal display.
            created_at: ISO format creation timestamp.
            total_time: Accumulated tracked time in seconds.
            entry_count: Number of associated time entries.
        """
        self.name: str = name
        self.description: str = description
        self.color: str = color
        self.created_at: str = created_at or datetime.now().isoformat()
        self.total_time: float = total_time
        self.entry_count: int = entry_count

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Project to a dictionary.

        Returns:
            Dictionary representation of this project.
        """
        return {
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": self.created_at,
            "total_time": self.total_time,
            "entry_count": self.entry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Deserialize a Project from a dictionary.

        Args:
            data: Dictionary containing project data.

        Returns:
            A new Project instance.
        """
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            color=data.get("color", "cyan"),
            created_at=data.get("created_at"),
            total_time=data.get("total_time", 0.0),
            entry_count=data.get("entry_count", 0),
        )

    def __repr__(self) -> str:
        """Return a string representation of the Project."""
        return f"Project(name='{self.name}', entries={self.entry_count})"


class Session:
    """Represents the current active tracking session.

    Stores the state of an in-progress time tracking session, including
    pause/resume history for accurate duration calculation.

    Attributes:
        entry: The TimeEntry being tracked.
        is_paused: Whether the session is currently paused.
        pause_start: When the current pause started (ISO format), if paused.
        pause_history: List of (pause_start, pause_end) ISO format pairs.
    """

    def __init__(self, entry: TimeEntry):
        """Initialize a Session with a TimeEntry.

        Args:
            entry: The TimeEntry to track in this session.
        """
        self.entry: TimeEntry = entry
        self.is_paused: bool = False
        self.pause_start: Optional[str] = None
        self.pause_history: List[Dict[str, str]] = []

    def pause(self) -> None:
        """Pause the current session.

        Records the pause start time. Does nothing if already paused.
        """
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = datetime.now().isoformat()

    def resume(self) -> float:
        """Resume the current session.

        Records the pause end time and adds to pause history.

        Returns:
            Duration of the pause in seconds.

        Raises:
            RuntimeError: If the session is not currently paused.
        """
        if not self.is_paused:
            raise RuntimeError("Cannot resume: session is not paused")
        pause_end = datetime.now().isoformat()
        pause_start_dt = datetime.fromisoformat(self.pause_start)
        pause_end_dt = datetime.fromisoformat(pause_end)
        pause_duration = (pause_end_dt - pause_start_dt).total_seconds()

        self.pause_history.append({
            "start": self.pause_start,
            "end": pause_end,
        })
        self.entry.paused_duration += pause_duration
        self.is_paused = False
        self.pause_start = None
        return pause_duration

    def get_total_paused(self) -> float:
        """Calculate total paused time including any active pause.

        Returns:
            Total paused time in seconds.
        """
        total = self.entry.paused_duration
        if self.is_paused and self.pause_start:
            total += (
                datetime.now() - datetime.fromisoformat(self.pause_start)
            ).total_seconds()
        return total

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Session to a dictionary.

        Returns:
            Dictionary representation of this session.
        """
        return {
            "entry": self.entry.to_dict(),
            "is_paused": self.is_paused,
            "pause_start": self.pause_start,
            "pause_history": self.pause_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Deserialize a Session from a dictionary.

        Args:
            data: Dictionary containing session data.

        Returns:
            A new Session instance.
        """
        entry = TimeEntry.from_dict(data["entry"])
        session = cls(entry)
        session.is_paused = data.get("is_paused", False)
        session.pause_start = data.get("pause_start")
        session.pause_history = data.get("pause_history", [])
        return session

    def __repr__(self) -> str:
        """Return a string representation of the Session."""
        status = "paused" if self.is_paused else "running"
        return (
            f"Session(project='{self.entry.project}', status={status})"
        )
