"""Tests for the Storage engine.

Tests cover data persistence, retrieval, update, deletion, and
project management operations using temporary directories.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from timeforge.core.models import TimeEntry, Project, Session
from timeforge.core.storage import Storage


class TestStorage(unittest.TestCase):
    """Test cases for the Storage class."""

    def setUp(self):
        """Set up a temporary storage directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(data_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temporary storage after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_directory_creation(self):
        """Test that the data directory is created."""
        self.assertTrue(self.storage.data_dir.exists())

    def test_add_and_load_entry(self):
        """Test adding and loading a time entry."""
        entry = TimeEntry(project="test-project", description="Test task")
        self.storage.add_entry(entry)

        entries = self.storage.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].project, "test-project")
        self.assertEqual(entries[0].description, "Test task")

    def test_load_entries_empty(self):
        """Test loading entries when storage is empty."""
        entries = self.storage.load_entries()
        self.assertEqual(len(entries), 0)

    def test_get_entry_by_id(self):
        """Test retrieving an entry by its ID."""
        entry = TimeEntry(project="my-project", entry_id="abc12345")
        self.storage.add_entry(entry)

        found = self.storage.get_entry("abc12345")
        self.assertIsNotNone(found)
        self.assertEqual(found.project, "my-project")

    def test_get_entry_nonexistent(self):
        """Test retrieving a non-existent entry."""
        found = self.storage.get_entry("nonexistent")
        self.assertIsNone(found)

    def test_update_entry(self):
        """Test updating an existing entry."""
        entry = TimeEntry(project="old-project", entry_id="upd001")
        self.storage.add_entry(entry)

        entry.project = "new-project"
        entry.description = "Updated"
        self.storage.update_entry(entry)

        found = self.storage.get_entry("upd001")
        self.assertEqual(found.project, "new-project")
        self.assertEqual(found.description, "Updated")

    def test_update_nonexistent_entry(self):
        """Test updating a non-existent entry raises ValueError."""
        entry = TimeEntry(project="ghost", entry_id="ghost01")
        with self.assertRaises(ValueError):
            self.storage.update_entry(entry)

    def test_delete_entry(self):
        """Test deleting an entry."""
        entry = TimeEntry(project="to-delete", entry_id="del001")
        self.storage.add_entry(entry)

        result = self.storage.delete_entry("del001")
        self.assertTrue(result)

        entries = self.storage.load_entries()
        self.assertEqual(len(entries), 0)

    def test_delete_nonexistent_entry(self):
        """Test deleting a non-existent entry."""
        result = self.storage.delete_entry("nonexistent")
        self.assertFalse(result)

    def test_get_entries_by_project(self):
        """Test filtering entries by project."""
        self.storage.add_entry(TimeEntry(project="alpha", entry_id="a1"))
        self.storage.add_entry(TimeEntry(project="beta", entry_id="b1"))
        self.storage.add_entry(TimeEntry(project="alpha", entry_id="a2"))

        alpha_entries = self.storage.get_entries_by_project("alpha")
        self.assertEqual(len(alpha_entries), 2)

        beta_entries = self.storage.get_entries_by_project("beta")
        self.assertEqual(len(beta_entries), 1)

    def test_get_entries_by_date(self):
        """Test filtering entries by date."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.storage.add_entry(
            TimeEntry(project="p1", start_time=f"{today}T10:00:00")
        )
        self.storage.add_entry(
            TimeEntry(project="p2", start_time="2025-06-01T10:00:00")
        )

        today_entries = self.storage.get_entries_by_date(today)
        self.assertEqual(len(today_entries), 1)

    def test_get_entries_by_date_range(self):
        """Test filtering entries by date range."""
        self.storage.add_entry(
            TimeEntry(project="p1", start_time="2025-06-01T10:00:00")
        )
        self.storage.add_entry(
            TimeEntry(project="p2", start_time="2025-06-05T10:00:00")
        )
        self.storage.add_entry(
            TimeEntry(project="p3", start_time="2025-06-10T10:00:00")
        )

        entries = self.storage.get_entries_by_date_range(
            "2025-06-01", "2025-06-05"
        )
        self.assertEqual(len(entries), 2)

    def test_project_operations(self):
        """Test project create, load, update, and delete."""
        # Create
        proj = self.storage.get_or_create_project("my-project")
        self.assertEqual(proj.name, "my-project")

        # Get existing
        proj2 = self.storage.get_or_create_project("my-project")
        self.assertEqual(proj2.name, "my-project")

        # Update
        proj.description = "A test project"
        self.storage.update_project(proj)
        projects = self.storage.load_projects()
        self.assertEqual(projects[0].description, "A test project")

        # Delete
        result = self.storage.delete_project("my-project")
        self.assertTrue(result)
        projects = self.storage.load_projects()
        self.assertEqual(len(projects), 0)

    def test_session_save_and_load(self):
        """Test saving and loading an active session."""
        entry = TimeEntry(project="session-project")
        session = Session(entry)
        session.pause()

        self.storage.save_session(session)
        loaded = self.storage.load_session()

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.entry.project, "session-project")
        self.assertTrue(loaded.is_paused)

    def test_session_clear(self):
        """Test clearing the active session."""
        entry = TimeEntry(project="temp")
        session = Session(entry)
        self.storage.save_session(session)
        self.storage.clear_session()

        loaded = self.storage.load_session()
        self.assertIsNone(loaded)

    def test_get_all_project_names(self):
        """Test getting all unique project names."""
        self.storage.add_entry(TimeEntry(project="alpha"))
        self.storage.add_entry(TimeEntry(project="beta"))
        self.storage.add_entry(TimeEntry(project="alpha"))

        names = self.storage.get_all_project_names()
        self.assertEqual(sorted(names), ["alpha", "beta"])

    def test_get_stats(self):
        """Test getting overall statistics."""
        self.storage.add_entry(
            TimeEntry(
                project="p1",
                start_time="2025-06-01T10:00:00",
                end_time="2025-06-01T12:00:00",
                duration=7200.0,
            )
        )
        self.storage.add_entry(
            TimeEntry(
                project="p2",
                start_time="2025-06-01T13:00:00",
                end_time="2025-06-01T14:00:00",
                duration=3600.0,
            )
        )

        stats = self.storage.get_stats()
        self.assertEqual(stats["total_entries"], 2)
        self.assertEqual(stats["total_projects"], 2)
        self.assertEqual(stats["total_time_seconds"], 10800.0)

    def test_export_data(self):
        """Test exporting all data."""
        self.storage.add_entry(TimeEntry(project="export-test"))
        self.storage.get_or_create_project("export-test")

        data = self.storage.export_data()
        self.assertIn("entries", data)
        self.assertIn("projects", data)
        self.assertIn("exported_at", data)
        self.assertEqual(len(data["entries"]), 1)

    def test_backup(self):
        """Test creating a data backup."""
        self.storage.add_entry(TimeEntry(project="backup-test"))

        backup_path = self.storage.backup()
        self.assertTrue(os.path.exists(backup_path))

        import json
        with open(backup_path, "r") as f:
            data = json.load(f)
        self.assertEqual(len(data["entries"]), 1)

    def test_multiple_entries_sorted(self):
        """Test that entries are loaded in descending start_time order."""
        self.storage.add_entry(
            TimeEntry(project="p", start_time="2025-01-01T10:00:00")
        )
        self.storage.add_entry(
            TimeEntry(project="p", start_time="2025-01-03T10:00:00")
        )
        self.storage.add_entry(
            TimeEntry(project="p", start_time="2025-01-02T10:00:00")
        )

        entries = self.storage.load_entries()
        self.assertEqual(entries[0].start_time, "2025-01-03T10:00:00")
        self.assertEqual(entries[1].start_time, "2025-01-02T10:00:00")
        self.assertEqual(entries[2].start_time, "2025-01-01T10:00:00")


if __name__ == "__main__":
    unittest.main()
