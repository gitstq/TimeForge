"""Time tracking core engine for TimeForge.

Provides the main tracking functionality including start, stop, pause,
resume, and status operations. Manages the active session and persists
data through the storage engine.
"""

import os
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import TimeEntry, Project, Session
from .storage import Storage
from ..utils.display import Display, Colors


class TimeTracker:
    """Core time tracking engine.

    Manages time tracking sessions including start, stop, pause, resume
    operations. Handles idle time detection and provides status information.

    Attributes:
        storage: The Storage engine instance for data persistence.
        display: The Display utility for terminal output.
    """

    IDLE_THRESHOLD_SECONDS = 300  # 5 minutes

    def __init__(self, storage: Optional[Storage] = None):
        """Initialize the TimeTracker.

        Args:
            storage: Custom Storage instance. Creates default if None.
        """
        self.storage = storage or Storage()
        self.display = Display()
        self._last_activity_time: Optional[float] = None
        self._check_idle_on_start()

    def _check_idle_on_start(self) -> None:
        """Check for idle time when starting the tracker.

        If there's an active session and the last activity was more than
        IDLE_THRESHOLD_SECONDS ago, prompt the user about the gap.
        """
        session = self.storage.load_session()
        if session and not session.is_paused:
            entry = session.entry
            last_updated = datetime.fromisoformat(entry.updated_at)
            idle_seconds = (datetime.now() - last_updated).total_seconds()
            if idle_seconds > self.IDLE_THRESHOLD_SECONDS:
                idle_minutes = int(idle_seconds / 60)
                self.display.warning(
                    f"Idle time detected: {idle_minutes} minutes since "
                    f"last activity on project '{entry.project}'.\n"
                    f"Consider stopping or pausing the current session."
                )

    def start(
        self, project: str, description: str = ""
    ) -> TimeEntry:
        """Start tracking time for a project.

        If there's an active session, it will be stopped first.

        Args:
            project: Name of the project to track.
            description: Optional description of the work.

        Returns:
            The newly created TimeEntry.
        """
        # Stop any existing session first
        existing_session = self.storage.load_session()
        if existing_session:
            self.stop()

        # Create new entry
        entry = TimeEntry(project=project, description=description)
        session = Session(entry)

        # Save session
        self.storage.save_session(session)

        # Ensure project exists
        self.storage.get_or_create_project(project)

        # Update activity time
        self._last_activity_time = time.time()

        self.display.success(
            f"Started tracking: {Colors.bold(project)}"
            + (f" - {description}" if description else "")
        )
        self.display.info(f"Entry ID: {entry.id}")

        return entry

    def stop(self) -> Optional[TimeEntry]:
        """Stop the current tracking session.

        Returns:
            The completed TimeEntry, or None if no session is active.
        """
        session = self.storage.load_session()
        if not session:
            self.display.warning("No active session to stop.")
            return None

        # If paused, resume first to record the pause duration
        if session.is_paused:
            session.resume()

        entry = session.entry
        entry.end_time = datetime.now().isoformat()
        entry.duration = entry.compute_duration()
        entry.updated_at = datetime.now().isoformat()

        # Save the completed entry
        self.storage.add_entry(entry)
        self.storage.clear_session()

        # Update project stats
        self._update_project_stats(entry.project)

        duration_str = self._format_duration(entry.duration)
        self.display.success(
            f"Stopped tracking: {Colors.bold(entry.project)} "
            f"- {duration_str}"
        )

        return entry

    def pause(self) -> bool:
        """Pause the current tracking session.

        Returns:
            True if paused successfully, False if no active session.
        """
        session = self.storage.load_session()
        if not session:
            self.display.warning("No active session to pause.")
            return False

        if session.is_paused:
            self.display.info("Session is already paused.")
            return False

        session.pause()
        self.storage.save_session(session)

        self.display.info(
            f"Paused tracking: {Colors.bold(session.entry.project)}"
        )
        return True

    def resume(self) -> bool:
        """Resume a paused tracking session.

        Returns:
            True if resumed successfully, False if no paused session.
        """
        session = self.storage.load_session()
        if not session:
            self.display.warning("No active session to resume.")
            return False

        if not session.is_paused:
            self.display.info("Session is not paused.")
            return False

        pause_duration = session.resume()
        self.storage.save_session(session)

        pause_str = self._format_duration(pause_duration)
        self.display.success(
            f"Resumed tracking: {Colors.bold(session.entry.project)} "
            f"(paused for {pause_str})"
        )
        return True

    def status(self) -> Optional[Dict[str, Any]]:
        """Get the current tracking status.

        Returns:
            Dictionary with status information, or None if no active session.
        """
        session = self.storage.load_session()
        if not session:
            self.display.info("No active tracking session.")
            return None

        entry = session.entry
        current_duration = entry.compute_duration()
        paused = session.get_total_paused()

        status_info = {
            "id": entry.id,
            "project": entry.project,
            "description": entry.description,
            "start_time": entry.start_time,
            "is_paused": session.is_paused,
            "current_duration": current_duration,
            "paused_duration": paused,
            "effective_duration": current_duration - paused,
        }

        # Display status
        state = Colors.yellow("PAUSED") if session.is_paused else Colors.green("RUNNING")
        self.display.info(f"Status: {state}")
        self.display.info(f"Project: {Colors.bold(entry.project)}")
        if entry.description:
            self.display.info(f"Description: {entry.description}")
        self.display.info(
            f"Started: {self._format_timestamp(entry.start_time)}"
        )
        self.display.info(
            f"Duration: {self._format_duration(current_duration)}"
        )
        if paused > 0:
            self.display.info(
                f"Paused: {self._format_duration(paused)}"
            )
        self.display.info(
            f"Effective: {self._format_duration(current_duration - paused)}"
        )

        return status_info

    def log(self, date: Optional[str] = None) -> List[TimeEntry]:
        """View time log for a specific date.

        Args:
            date: Date in YYYY-MM-DD format. Defaults to today.

        Returns:
            List of TimeEntry objects for the specified date.
        """
        entries = self.storage.get_entries_by_date(date)
        if not entries:
            date_str = date or datetime.now().strftime("%Y-%m-%d")
            self.display.info(f"No entries found for {date_str}.")
            return entries

        # Sort by start_time ascending for display
        entries.sort(key=lambda e: e.start_time)

        date_str = date or datetime.now().strftime("%Y-%m-%d")
        self.display.header(f"Time Log - {date_str}")

        total = 0.0
        rows = []
        for entry in entries:
            duration = entry.compute_duration()
            total += duration
            rows.append([
                entry.id,
                entry.project,
                entry.description[:30] if entry.description else "-",
                self._format_time(entry.start_time),
                self._format_time(entry.end_time) if entry.end_time else "active",
                self._format_duration(duration),
            ])

        self.display.table(
            ["ID", "Project", "Description", "Start", "End", "Duration"],
            rows,
        )
        self.display.info(f"Total: {self._format_duration(total)}")

        return entries

    def list_projects(self) -> List[Project]:
        """List all projects with their statistics.

        Returns:
            List of Project objects with updated statistics.
        """
        entries = self.storage.load_entries()
        project_stats: Dict[str, Dict[str, Any]] = {}

        for entry in entries:
            name = entry.project
            if name not in project_stats:
                project_stats[name] = {
                    "total_time": 0.0,
                    "entry_count": 0,
                }
            project_stats[name]["total_time"] += entry.compute_duration()
            project_stats[name]["entry_count"] += 1

        projects = self.storage.load_projects()
        # Update project stats from entries
        updated_projects = []
        for proj in projects:
            if proj.name in project_stats:
                proj.total_time = project_stats[proj.name]["total_time"]
                proj.entry_count = project_stats[proj.name]["entry_count"]
            updated_projects.append(proj)

        # Add projects that exist in entries but not in projects file
        existing_names = {p.name for p in projects}
        for name, stats in project_stats.items():
            if name not in existing_names:
                proj = Project(
                    name=name,
                    total_time=stats["total_time"],
                    entry_count=stats["entry_count"],
                )
                updated_projects.append(proj)

        if not updated_projects:
            self.display.info("No projects found.")
            return []

        self.display.header("Projects")

        rows = []
        for proj in sorted(updated_projects, key=lambda p: p.total_time, reverse=True):
            rows.append([
                proj.name,
                str(proj.entry_count),
                self._format_duration(proj.total_time),
                proj.description[:30] if proj.description else "-",
            ])

        self.display.table(
            ["Project", "Entries", "Total Time", "Description"],
            rows,
        )

        return updated_projects

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a time entry by ID.

        Args:
            entry_id: The unique identifier of the entry.

        Returns:
            True if the entry was deleted, False otherwise.
        """
        entry = self.storage.get_entry(entry_id)
        if not entry:
            self.display.error(f"Entry '{entry_id}' not found.")
            return False

        if self.storage.delete_entry(entry_id):
            self.display.success(f"Deleted entry '{entry_id}'.")
            return True
        return False

    def edit_entry(
        self,
        entry_id: str,
        project: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> bool:
        """Edit a time entry.

        Args:
            entry_id: The unique identifier of the entry.
            project: New project name, or None to keep current.
            description: New description, or None to keep current.
            start_time: New start time (ISO format), or None to keep current.
            end_time: New end time (ISO format), or None to keep current.

        Returns:
            True if the entry was updated, False otherwise.
        """
        entry = self.storage.get_entry(entry_id)
        if not entry:
            self.display.error(f"Entry '{entry_id}' not found.")
            return False

        if project:
            entry.project = project
        if description is not None:
            entry.description = description
        if start_time:
            entry.start_time = start_time
        if end_time is not None:
            entry.end_time = end_time

        entry.duration = entry.compute_duration()
        entry.updated_at = datetime.now().isoformat()

        self.storage.update_entry(entry)
        self.display.success(f"Updated entry '{entry_id}'.")
        return True

    def _update_project_stats(self, project_name: str) -> None:
        """Update project statistics after an entry is completed.

        Args:
            project_name: Name of the project to update.
        """
        entries = self.storage.get_entries_by_project(project_name)
        total_time = sum(e.compute_duration() for e in entries)
        project = self.storage.get_or_create_project(project_name)
        project.total_time = total_time
        project.entry_count = len(entries)
        self.storage.update_project(project)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format a duration in seconds to a human-readable string.

        Args:
            seconds: Duration in seconds.

        Returns:
            Formatted string like '2h 30m 15s'.
        """
        if seconds < 0:
            seconds = 0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        return " ".join(parts)

    @staticmethod
    def _format_timestamp(iso_string: str) -> str:
        """Format an ISO timestamp for display.

        Args:
            iso_string: ISO format timestamp string.

        Returns:
            Formatted timestamp string.
        """
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return iso_string

    @staticmethod
    def _format_time(iso_string: Optional[str]) -> str:
        """Format an ISO timestamp to show only time.

        Args:
            iso_string: ISO format timestamp string.

        Returns:
            Formatted time string (HH:MM).
        """
        if not iso_string:
            return "-"
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%H:%M")
        except (ValueError, TypeError):
            return iso_string
