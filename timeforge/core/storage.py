"""JSON file storage engine for TimeForge.

Handles all persistent data storage operations using JSON files.
Data is stored in ~/.timeforge/ directory with separate files for
time entries, projects, and the active session.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import TimeEntry, Project, Session


class Storage:
    """JSON-based storage engine for TimeForge data.

    Manages persistence of time entries, projects, and active sessions
    to JSON files in the user's home directory (~/.timeforge/).

    Attributes:
        data_dir: Path to the TimeForge data directory.
        entries_file: Path to the time entries JSON file.
        projects_file: Path to the projects JSON file.
        session_file: Path to the active session JSON file.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the Storage engine.

        Creates the data directory and files if they don't exist.

        Args:
            data_dir: Custom data directory path. Defaults to ~/.timeforge.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path.home() / ".timeforge"

        self.entries_file = self.data_dir / "data.json"
        self.projects_file = self.data_dir / "projects.json"
        self.session_file = self.data_dir / "session.json"

        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Create the data directory if it does not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, filepath: Path) -> Any:
        """Read and parse a JSON file.

        Args:
            filepath: Path to the JSON file.

        Returns:
            Parsed JSON data, or None if file doesn't exist.
        """
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _write_json(self, filepath: Path, data: Any) -> None:
        """Write data to a JSON file with atomic write (write to temp then rename).

        Args:
            filepath: Path to the JSON file.
            data: Data to serialize and write.
        """
        self._ensure_directory()
        temp_file = filepath.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            shutil.move(str(temp_file), str(filepath))
        except IOError:
            if temp_file.exists():
                temp_file.unlink()
            raise

    # ── TimeEntry operations ──────────────────────────────────────────

    def load_entries(self) -> List[TimeEntry]:
        """Load all time entries from storage.

        Returns:
            List of TimeEntry objects, sorted by start_time descending.
        """
        data = self._read_json(self.entries_file)
        if not data:
            return []
        entries = [TimeEntry.from_dict(e) for e in data.get("entries", [])]
        entries.sort(key=lambda e: e.start_time, reverse=True)
        return entries

    def save_entries(self, entries: List[TimeEntry]) -> None:
        """Save all time entries to storage.

        Args:
            entries: List of TimeEntry objects to persist.
        """
        data = {
            "entries": [e.to_dict() for e in entries],
            "last_updated": datetime.now().isoformat(),
        }
        self._write_json(self.entries_file, data)

    def add_entry(self, entry: TimeEntry) -> None:
        """Add a new time entry to storage.

        Args:
            entry: The TimeEntry to add.
        """
        entries = self.load_entries()
        entries.append(entry)
        self.save_entries(entries)

    def get_entry(self, entry_id: str) -> Optional[TimeEntry]:
        """Get a specific time entry by ID.

        Args:
            entry_id: The unique identifier of the entry.

        Returns:
            The matching TimeEntry, or None if not found.
        """
        entries = self.load_entries()
        for entry in entries:
            if entry.id == entry_id:
                return entry
        return None

    def update_entry(self, entry: TimeEntry) -> None:
        """Update an existing time entry in storage.

        Args:
            entry: The TimeEntry with updated data.

        Raises:
            ValueError: If the entry with the given ID is not found.
        """
        entries = self.load_entries()
        found = False
        for i, existing in enumerate(entries):
            if existing.id == entry.id:
                entry.updated_at = datetime.now().isoformat()
                entries[i] = entry
                found = True
                break
        if not found:
            raise ValueError(f"Entry '{entry.id}' not found")
        self.save_entries(entries)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a time entry by ID.

        Args:
            entry_id: The unique identifier of the entry to delete.

        Returns:
            True if the entry was deleted, False if not found.
        """
        entries = self.load_entries()
        original_count = len(entries)
        entries = [e for e in entries if e.id != entry_id]
        if len(entries) < original_count:
            self.save_entries(entries)
            return True
        return False

    def get_entries_by_project(self, project: str) -> List[TimeEntry]:
        """Get all time entries for a specific project.

        Args:
            project: The project name to filter by.

        Returns:
            List of TimeEntry objects for the given project.
        """
        entries = self.load_entries()
        return [e for e in entries if e.project == project]

    def get_entries_by_date(
        self, date: Optional[str] = None
    ) -> List[TimeEntry]:
        """Get time entries for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format. Defaults to today.

        Returns:
            List of TimeEntry objects for the given date.
        """
        if date is None:
            target = datetime.now().strftime("%Y-%m-%d")
        else:
            target = date
        entries = self.load_entries()
        result = []
        for entry in entries:
            entry_date = entry.start_time[:10]
            if entry_date == target:
                result.append(entry)
        return result

    def get_entries_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[TimeEntry]:
        """Get time entries within a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive).
            end_date: End date in YYYY-MM-DD format (inclusive).

        Returns:
            List of TimeEntry objects within the date range.
        """
        entries = self.load_entries()
        result = []
        for entry in entries:
            entry_date = entry.start_time[:10]
            if start_date <= entry_date <= end_date:
                result.append(entry)
        return result

    # ── Project operations ────────────────────────────────────────────

    def load_projects(self) -> List[Project]:
        """Load all projects from storage.

        Returns:
            List of Project objects.
        """
        data = self._read_json(self.projects_file)
        if not data:
            return []
        return [Project.from_dict(p) for p in data.get("projects", [])]

    def save_projects(self, projects: List[Project]) -> None:
        """Save all projects to storage.

        Args:
            projects: List of Project objects to persist.
        """
        data = {
            "projects": [p.to_dict() for p in projects],
            "last_updated": datetime.now().isoformat(),
        }
        self._write_json(self.projects_file, data)

    def get_or_create_project(self, name: str) -> Project:
        """Get an existing project or create a new one.

        Args:
            name: The project name.

        Returns:
            The existing or newly created Project.
        """
        projects = self.load_projects()
        for project in projects:
            if project.name == name:
                return project
        new_project = Project(name=name)
        projects.append(new_project)
        self.save_projects(projects)
        return new_project

    def update_project(self, project: Project) -> None:
        """Update an existing project's metadata.

        Args:
            project: The Project with updated data.
        """
        projects = self.load_projects()
        for i, existing in enumerate(projects):
            if existing.name == project.name:
                projects[i] = project
                break
        self.save_projects(projects)

    def delete_project(self, name: str) -> bool:
        """Delete a project by name.

        Args:
            name: The project name to delete.

        Returns:
            True if the project was deleted, False if not found.
        """
        projects = self.load_projects()
        original_count = len(projects)
        projects = [p for p in projects if p.name != name]
        if len(projects) < original_count:
            self.save_projects(projects)
            return True
        return False

    # ── Session operations ────────────────────────────────────────────

    def save_session(self, session: Optional[Session]) -> None:
        """Save the active session to storage.

        Args:
            session: The Session to save, or None to clear.
        """
        if session is None:
            if self.session_file.exists():
                self.session_file.unlink()
            return
        data = session.to_dict()
        self._write_json(self.session_file, data)

    def load_session(self) -> Optional[Session]:
        """Load the active session from storage.

        Returns:
            The active Session, or None if no session is active.
        """
        data = self._read_json(self.session_file)
        if not data:
            return None
        try:
            return Session.from_dict(data)
        except (KeyError, TypeError):
            return None

    def clear_session(self) -> None:
        """Remove the active session from storage."""
        if self.session_file.exists():
            self.session_file.unlink()

    # ── Utility operations ────────────────────────────────────────────

    def get_all_project_names(self) -> List[str]:
        """Get a list of all unique project names from entries.

        Returns:
            Sorted list of unique project names.
        """
        entries = self.load_entries()
        names = set(e.project for e in entries)
        return sorted(names)

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics from stored data.

        Returns:
            Dictionary containing total entries, projects, and time.
        """
        entries = self.load_entries()
        total_time = sum(e.compute_duration() for e in entries)
        projects = self.get_all_project_names()
        return {
            "total_entries": len(entries),
            "total_projects": len(projects),
            "total_time_seconds": total_time,
            "projects": projects,
        }

    def export_data(self) -> Dict[str, Any]:
        """Export all stored data as a dictionary.

        Returns:
            Dictionary containing all entries, projects, and session.
        """
        return {
            "entries": [e.to_dict() for e in self.load_entries()],
            "projects": [p.to_dict() for p in self.load_projects()],
            "session": self.load_session(),
            "exported_at": datetime.now().isoformat(),
        }

    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of all data.

        Args:
            backup_path: Custom backup file path. Auto-generated if None.

        Returns:
            Path to the created backup file.
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(
                self.data_dir / f"backup_{timestamp}.json"
            )
        data = self.export_data()
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return backup_path
