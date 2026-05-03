"""Tests for the TimeTracker core engine.

Tests cover start, stop, pause, resume, status, log, list, delete,
and edit operations using a temporary storage directory.
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
from timeforge.core.tracker import TimeTracker


class TestTimeTracker(unittest.TestCase):
    """Test cases for the TimeTracker class."""

    def setUp(self):
        """Set up a temporary storage directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(data_dir=self.temp_dir)
        self.tracker = TimeTracker(storage=self.storage)

    def tearDown(self):
        """Clean up temporary storage after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_start_tracking(self):
        """Test starting a new tracking session."""
        entry = self.tracker.start("test-project", "Test description")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.project, "test-project")
        self.assertEqual(entry.description, "Test description")
        self.assertTrue(entry.is_active)

        # Verify session is saved
        session = self.storage.load_session()
        self.assertIsNotNone(session)
        self.assertEqual(session.entry.project, "test-project")

    def test_start_without_description(self):
        """Test starting tracking without a description."""
        entry = self.tracker.start("myproject")
        self.assertEqual(entry.project, "myproject")
        self.assertEqual(entry.description, "")

    def test_stop_tracking(self):
        """Test stopping an active tracking session."""
        self.tracker.start("test-project")
        entry = self.tracker.stop()
        self.assertIsNotNone(entry)
        self.assertFalse(entry.is_active)
        self.assertIsNotNone(entry.end_time)
        self.assertGreater(entry.duration, 0)

        # Verify session is cleared
        session = self.storage.load_session()
        self.assertIsNone(session)

        # Verify entry is saved
        entries = self.storage.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].project, "test-project")

    def test_stop_no_active_session(self):
        """Test stopping when no session is active."""
        entry = self.tracker.stop()
        self.assertIsNone(entry)

    def test_pause_and_resume(self):
        """Test pausing and resuming a session."""
        self.tracker.start("test-project")

        # Pause
        result = self.tracker.pause()
        self.assertTrue(result)

        session = self.storage.load_session()
        self.assertTrue(session.is_paused)

        # Resume
        result = self.tracker.resume()
        self.assertTrue(result)

        session = self.storage.load_session()
        self.assertFalse(session.is_paused)
        self.assertGreater(session.entry.paused_duration, 0)

    def test_pause_already_paused(self):
        """Test pausing when already paused."""
        self.tracker.start("test-project")
        self.tracker.pause()
        result = self.tracker.pause()
        self.assertFalse(result)

    def test_resume_not_paused(self):
        """Test resuming when not paused."""
        self.tracker.start("test-project")
        result = self.tracker.resume()
        self.assertFalse(result)

    def test_status_active(self):
        """Test getting status of an active session."""
        self.tracker.start("test-project", "Working on stuff")
        status = self.tracker.status()
        self.assertIsNotNone(status)
        self.assertEqual(status["project"], "test-project")
        self.assertEqual(status["description"], "Working on stuff")
        self.assertFalse(status["is_paused"])
        self.assertGreater(status["current_duration"], 0)

    def test_status_no_session(self):
        """Test getting status when no session is active."""
        status = self.tracker.status()
        self.assertIsNone(status)

    def test_status_paused(self):
        """Test getting status of a paused session."""
        self.tracker.start("test-project")
        self.tracker.pause()
        status = self.tracker.status()
        self.assertIsNotNone(status)
        self.assertTrue(status["is_paused"])

    def test_log_today(self):
        """Test viewing today's time log."""
        self.tracker.start("proj-a", "Task A")
        self.tracker.stop()
        self.tracker.start("proj-b", "Task B")
        self.tracker.stop()

        entries = self.tracker.log()
        self.assertEqual(len(entries), 2)

    def test_log_specific_date(self):
        """Test viewing time log for a specific date."""
        # Create an entry with a specific date
        past_date = "2025-01-15T10:00:00"
        entry = TimeEntry(
            project="old-project",
            description="Old task",
            start_time=past_date,
            end_time="2025-01-15T11:00:00",
            duration=3600.0,
        )
        self.storage.add_entry(entry)

        entries = self.tracker.log("2025-01-15")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].project, "old-project")

    def test_log_empty(self):
        """Test viewing log when no entries exist."""
        entries = self.tracker.log("2099-01-01")
        self.assertEqual(len(entries), 0)

    def test_list_projects(self):
        """Test listing all projects."""
        self.tracker.start("alpha")
        self.tracker.stop()
        self.tracker.start("beta")
        self.tracker.stop()
        self.tracker.start("alpha")
        self.tracker.stop()

        projects = self.tracker.list_projects()
        self.assertEqual(len(projects), 2)

    def test_list_projects_empty(self):
        """Test listing projects when none exist."""
        projects = self.tracker.list_projects()
        self.assertEqual(len(projects), 0)

    def test_delete_entry(self):
        """Test deleting a time entry."""
        entry = self.tracker.start("test-project")
        self.tracker.stop()

        result = self.tracker.delete_entry(entry.id)
        self.assertTrue(result)

        # Verify entry is deleted
        entries = self.storage.load_entries()
        self.assertEqual(len(entries), 0)

    def test_delete_nonexistent_entry(self):
        """Test deleting a non-existent entry."""
        result = self.tracker.delete_entry("nonexistent")
        self.assertFalse(result)

    def test_edit_entry(self):
        """Test editing a time entry."""
        entry = self.tracker.start("old-project", "Old desc")
        self.tracker.stop()

        result = self.tracker.edit_entry(
            entry_id=entry.id,
            project="new-project",
            description="New desc",
        )
        self.assertTrue(result)

        # Verify changes
        updated = self.storage.get_entry(entry.id)
        self.assertEqual(updated.project, "new-project")
        self.assertEqual(updated.description, "New desc")

    def test_edit_nonexistent_entry(self):
        """Test editing a non-existent entry."""
        result = self.tracker.edit_entry("nonexistent", project="x")
        self.assertFalse(result)

    def test_start_replaces_active_session(self):
        """Test that starting a new session stops the previous one."""
        self.tracker.start("first-project")
        self.tracker.start("second-project")

        # First entry should be saved
        entries = self.storage.load_entries()
        completed = [e for e in entries if not e.is_active]
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].project, "first-project")

        # Second should be active
        session = self.storage.load_session()
        self.assertEqual(session.entry.project, "second-project")

    def test_stop_auto_resumes_pause(self):
        """Test that stopping auto-resumes a paused session."""
        self.tracker.start("test-project")
        self.tracker.pause()

        import time
        time.sleep(0.1)

        entry = self.tracker.stop()
        self.assertIsNotNone(entry)
        self.assertGreater(entry.paused_duration, 0)

    def test_format_duration(self):
        """Test duration formatting."""
        self.assertEqual(TimeTracker._format_duration(0), "0s")
        self.assertEqual(TimeTracker._format_duration(45), "45s")
        self.assertEqual(TimeTracker._format_duration(90), "1m 30s")
        self.assertEqual(TimeTracker._format_duration(3665), "1h 1m 5s")
        self.assertEqual(TimeTracker._format_duration(7200), "2h")


if __name__ == "__main__":
    unittest.main()
