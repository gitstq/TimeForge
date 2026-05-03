"""Tests for the Analytics Engine.

Tests cover productivity analysis calculations including streaks,
efficiency scoring, project distribution, and suggestion generation.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from timeforge.core.models import TimeEntry
from timeforge.core.storage import Storage
from timeforge.features.analytics import AnalyticsEngine


class TestAnalyticsEngine(unittest.TestCase):
    """Test cases for the AnalyticsEngine class."""

    def setUp(self):
        """Set up a temporary storage with sample data."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(data_dir=self.temp_dir)
        self.engine = AnalyticsEngine(storage=self.storage)

    def tearDown(self):
        """Clean up temporary storage."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _add_entry(self, days_ago: int, hours: float, project: str = "default") -> None:
        """Helper to add a time entry N days ago.

        Args:
            days_ago: How many days ago the entry was.
            hours: Duration in hours.
            project: Project name.
        """
        date = datetime.now() - timedelta(days=days_ago)
        start = date.replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=hours)
        entry = TimeEntry(
            project=project,
            start_time=start.isoformat(),
            end_time=end.isoformat(),
            duration=hours * 3600,
        )
        self.storage.add_entry(entry)

    def test_analyze_empty_data(self):
        """Test analysis with no data returns empty dict."""
        result = self.engine.analyze(days=30)
        self.assertEqual(result, {})

    def test_analyze_basic_stats(self):
        """Test basic analysis statistics."""
        self._add_entry(0, 2.0, "project-a")
        self._add_entry(0, 3.0, "project-b")
        self._add_entry(1, 4.0, "project-a")

        result = self.engine.analyze(days=7)
        self.assertEqual(result["total_entries"], 3)
        self.assertAlmostEqual(result["total_time"], 9 * 3600, places=0)
        self.assertEqual(len(result["project_distribution"]), 2)

    def test_analyze_project_distribution(self):
        """Test project distribution calculation."""
        self._add_entry(0, 6.0, "alpha")
        self._add_entry(0, 2.0, "beta")
        self._add_entry(1, 2.0, "alpha")

        result = self.engine.analyze(days=7)
        projects = {p["name"]: p for p in result["project_distribution"]}

        self.assertIn("alpha", projects)
        self.assertIn("beta", projects)
        self.assertEqual(projects["alpha"]["entry_count"], 2)
        self.assertEqual(projects["beta"]["entry_count"], 1)

        # Alpha: 8h, Beta: 2h, Total: 10h
        self.assertAlmostEqual(projects["alpha"]["percentage"], 80.0, places=1)
        self.assertAlmostEqual(projects["beta"]["percentage"], 20.0, places=1)

    def test_analyze_daily_stats(self):
        """Test daily statistics calculation."""
        self._add_entry(0, 3.0)
        self._add_entry(0, 2.0)
        self._add_entry(1, 4.0)

        result = self.engine.analyze(days=7)
        daily = result["daily_stats"]

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        self.assertIn(today, daily)
        self.assertIn(yesterday, daily)
        self.assertAlmostEqual(daily[today]["total_time"], 5 * 3600, places=0)
        self.assertAlmostEqual(daily[yesterday]["total_time"], 4 * 3600, places=0)

    def test_analyze_hourly_distribution(self):
        """Test hourly distribution calculation."""
        # Add entry at different hours
        date = datetime.now() - timedelta(days=1)
        morning_start = date.replace(hour=9, minute=0, second=0)
        morning_end = morning_start + timedelta(hours=2)
        self.storage.add_entry(TimeEntry(
            project="test",
            start_time=morning_start.isoformat(),
            end_time=morning_end.isoformat(),
            duration=7200.0,
        ))

        afternoon_start = date.replace(hour=14, minute=0, second=0)
        afternoon_end = afternoon_start + timedelta(hours=3)
        self.storage.add_entry(TimeEntry(
            project="test",
            start_time=afternoon_start.isoformat(),
            end_time=afternoon_end.isoformat(),
            duration=10800.0,
        ))

        result = self.engine.analyze(days=7)
        hourly = result["hourly_distribution"]

        self.assertIn(9, hourly)
        self.assertIn(14, hourly)
        self.assertAlmostEqual(hourly[14], 10800.0, places=0)

    def test_analyze_weekday_distribution(self):
        """Test weekday distribution calculation."""
        self._add_entry(0, 4.0)

        result = self.engine.analyze(days=7)
        weekday_dist = result["weekday_distribution"]

        today_weekday = datetime.now().weekday()
        today_data = [w for w in weekday_dist if w["day_num"] == today_weekday]
        self.assertEqual(len(today_data), 1)
        self.assertGreater(today_data[0]["total_time"], 0)

    def test_streak_calculation(self):
        """Test streak calculation."""
        # Add entries for consecutive days
        for i in range(5):
            self._add_entry(i, 2.0)

        result = self.engine.analyze(days=30)
        self.assertEqual(result["streak"], 5)
        self.assertGreaterEqual(result["longest_streak"], 5)

    def test_broken_streak(self):
        """Test streak with a gap."""
        self._add_entry(0, 2.0)
        self._add_entry(1, 2.0)
        # Day 2 has no entry (gap)
        self._add_entry(3, 2.0)

        result = self.engine.analyze(days=30)
        self.assertEqual(result["streak"], 2)  # Only today + yesterday

    def test_efficiency_score(self):
        """Test efficiency score calculation."""
        # Consistent daily work should give a decent score
        for i in range(7):
            self._add_entry(i, 6.0)

        result = self.engine.analyze(days=7)
        score = result["efficiency_score"]
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)

    def test_efficiency_score_low_activity(self):
        """Test efficiency score with minimal activity."""
        self._add_entry(0, 0.5)

        result = self.engine.analyze(days=30)
        score = result["efficiency_score"]
        # Should be low due to inconsistency
        self.assertLess(score, 50)

    def test_suggestions_generated(self):
        """Test that suggestions are generated."""
        self._add_entry(0, 4.0, "main-project")
        self._add_entry(1, 5.0, "main-project")

        result = self.engine.analyze(days=7)
        suggestions = result["suggestions"]
        self.assertGreater(len(suggestions), 0)

    def test_suggestions_peak_hour(self):
        """Test suggestion about peak productivity hour."""
        date = datetime.now() - timedelta(days=1)
        start = date.replace(hour=10, minute=0, second=0)
        end = start + timedelta(hours=4)
        self.storage.add_entry(TimeEntry(
            project="test",
            start_time=start.isoformat(),
            end_time=end.isoformat(),
            duration=14400.0,
        ))

        result = self.engine.analyze(days=7)
        suggestions = result["suggestions"]
        # Should mention peak hour
        has_peak_suggestion = any("productive" in s.lower() for s in suggestions)
        self.assertTrue(has_peak_suggestion)

    def test_analyze_custom_days(self):
        """Test analysis with custom day range."""
        for i in range(60):
            self._add_entry(i, 1.0)

        result_30 = self.engine.analyze(days=30)
        result_60 = self.engine.analyze(days=60)

        # range(60) creates entries for days 0-59
        # days=30: cutoff is 30 days ago, includes days 0-30 = 31 entries
        self.assertEqual(result_30["total_entries"], 31)
        # days=60: cutoff is 60 days ago, includes days 0-59 = 60 entries
        self.assertEqual(result_60["total_entries"], 60)

    def test_single_entry_analysis(self):
        """Test analysis with a single entry."""
        self._add_entry(0, 3.0)

        result = self.engine.analyze(days=7)
        self.assertEqual(result["total_entries"], 1)
        self.assertEqual(result["streak"], 1)
        self.assertGreater(len(result["suggestions"]), 0)


if __name__ == "__main__":
    unittest.main()
