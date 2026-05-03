"""Git commit linking feature for TimeForge.

Provides functionality to associate git commits with time tracking
entries, enabling correlation between code changes and time spent.
"""

import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.models import TimeEntry
from ..core.storage import Storage
from ..utils.display import Display, Colors


class GitLinker:
    """Git commit linker for TimeForge.

    Associates git commits with time tracking entries and provides
    views that combine time data with git history.

    Attributes:
        storage: The Storage engine instance for data access.
        display: The Display utility for terminal output.
    """

    def __init__(self, storage: Optional[Storage] = None):
        """Initialize the GitLinker.

        Args:
            storage: Custom Storage instance. Creates default if None.
        """
        self.storage = storage or Storage()
        self.display = Display()

    def find_git_root(self, path: Optional[str] = None) -> Optional[str]:
        """Find the root directory of the current git repository.

        Searches from the given path (or current working directory)
        upwards for a .git directory.

        Args:
            path: Starting path for the search. Defaults to cwd.

        Returns:
            Path to the git root directory, or None if not found.
        """
        start_path = path or os.getcwd()
        current = os.path.abspath(start_path)

        while True:
            git_dir = os.path.join(current, ".git")
            if os.path.isdir(git_dir):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                return None
            current = parent

    def get_latest_commit(
        self, repo_path: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """Get the latest git commit information.

        Args:
            repo_path: Path to the git repository. Auto-detected if None.

        Returns:
            Dictionary with commit hash, message, author, and date,
            or None if git is not available or no commits exist.
        """
        root = repo_path or self.find_git_root()
        if not root:
            return None

        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H%n%h%n%s%n%an%n%aI"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            lines = result.stdout.strip().split("\n")
            if len(lines) < 5:
                return None

            return {
                "hash": lines[0],
                "short_hash": lines[1],
                "message": lines[2],
                "author": lines[3],
                "date": lines[4],
            }
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def get_recent_commits(
        self, count: int = 10, repo_path: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Get recent git commits.

        Args:
            count: Number of commits to retrieve.
            repo_path: Path to the git repository. Auto-detected if None.

        Returns:
            List of commit dictionaries.
        """
        root = repo_path or self.find_git_root()
        if not root:
            return []

        try:
            result = subprocess.run(
                [
                    "git", "log", f"-{count}",
                    "--format=%H%n%h%n%s%n%an%n%aI",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return []

            commits = []
            lines = result.stdout.strip().split("\n")
            i = 0
            while i + 4 < len(lines):
                commits.append({
                    "hash": lines[i],
                    "short_hash": lines[i + 1],
                    "message": lines[i + 2],
                    "author": lines[i + 3],
                    "date": lines[i + 4],
                })
                i += 5

            return commits
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return []

    def link_commit(
        self, entry_id: Optional[str] = None
    ) -> bool:
        """Link the latest git commit to a time entry.

        If no entry_id is specified, links to the currently active session
        or the most recent completed entry.

        Args:
            entry_id: Specific entry ID to link. Auto-detected if None.

        Returns:
            True if the link was created successfully, False otherwise.
        """
        # Find git repo
        root = self.find_git_root()
        if not root:
            self.display.error(
                "Not in a git repository. "
                "Navigate to a git repo and try again."
            )
            return False

        # Get latest commit
        commit = self.get_latest_commit(root)
        if not commit:
            self.display.error("No git commits found.")
            return False

        # Find the target entry
        entry = self._find_target_entry(entry_id)
        if not entry:
            self.display.error("No time entry found to link.")
            return False

        # Check if already linked
        if commit["hash"] in entry.git_commits:
            self.display.info(
                f"Commit {commit['short_hash']} is already linked "
                f"to entry {entry.id}."
            )
            return True

        # Add the commit link
        entry.git_commits.append(commit["hash"])
        entry.updated_at = datetime.now().isoformat()
        self.storage.update_entry(entry)

        self.display.success(
            f"Linked commit {Colors.bold(commit['short_hash'])} "
            f"({commit['message'][:50]}) to entry {Colors.bold(entry.id)} "
            f"({entry.project})"
        )
        return True

    def show_git_log(self) -> None:
        """Display a combined view of git commits and time entries.

        Shows recent commits alongside any associated time tracking data.
        """
        root = self.find_git_root()
        if not root:
            self.display.error(
                "Not in a git repository. "
                "Navigate to a git repo and try again."
            )
            return

        commits = self.get_recent_commits(15, root)
        if not commits:
            self.display.error("No git commits found.")
            return

        entries = self.storage.load_entries()

        # Build a lookup from commit hash to entry
        commit_to_entry: Dict[str, TimeEntry] = {}
        for entry in entries:
            for ch in entry.git_commits:
                commit_to_entry[ch] = entry

        self.display.header("Git Log with Time Tracking")

        rows = []
        for commit in commits:
            linked_entry = commit_to_entry.get(commit["hash"])
            if linked_entry:
                duration = linked_entry.compute_duration()
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                time_str = f"{hours}h {minutes}m"
                project_str = linked_entry.project
            else:
                time_str = Colors.dim("-")
                project_str = Colors.dim("-")

            # Truncate commit message
            msg = commit["message"][:45]
            commit_date = commit["date"][:16].replace("T", " ")

            rows.append([
                commit["short_hash"],
                msg,
                project_str,
                time_str,
                commit_date,
            ])

        self.display.table(
            ["Hash", "Message", "Project", "Time", "Date"],
            rows,
        )

    def _find_target_entry(
        self, entry_id: Optional[str] = None
    ) -> Optional[TimeEntry]:
        """Find the target time entry for linking.

        Args:
            entry_id: Specific entry ID, or None for auto-detection.

        Returns:
            The target TimeEntry, or None if not found.
        """
        if entry_id:
            return self.storage.get_entry(entry_id)

        # Try active session first
        session = self.storage.load_session()
        if session:
            return session.entry

        # Fall back to most recent entry
        entries = self.storage.load_entries()
        if entries:
            return entries[0]

        return None
