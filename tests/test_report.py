"""Tests for the Report Generator.

Tests cover report generation in all supported formats (JSON, CSV,
HTML, Markdown) with various filtering options.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from timeforge.core.models import TimeEntry
from timeforge.core.storage import Storage
from timeforge.features.report import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class."""

    def setUp(self):
        """Set up a temporary storage with sample data."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(data_dir=self.temp_dir)
        self.generator = ReportGenerator(storage=self.storage)

        # Add sample entries
        today = datetime.now().strftime("%Y-%m-%d")
        self.storage.add_entry(TimeEntry(
            project="project-alpha",
            description="Design review meeting",
            start_time=f"{today}T09:00:00",
            end_time=f"{today}T10:30:00",
            duration=5400.0,
            entry_id="e001",
        ))
        self.storage.add_entry(TimeEntry(
            project="project-alpha",
            description="Code implementation",
            start_time=f"{today}T11:00:00",
            end_time=f"{today}T13:00:00",
            duration=7200.0,
            entry_id="e002",
        ))
        self.storage.add_entry(TimeEntry(
            project="project-beta",
            description="Documentation",
            start_time=f"{today}T14:00:00",
            end_time=f"{today}T15:00:00",
            duration=3600.0,
            entry_id="e003",
        ))

    def tearDown(self):
        """Clean up temporary storage."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_json_report(self):
        """Test generating a JSON format report."""
        report = self.generator.generate(
            period="daily", format_type="json"
        )
        self.assertIn('"period":', report)
        self.assertIn('"total_entries":', report)
        self.assertIn('"project-alpha"', report)
        self.assertIn('"project-beta"', report)

        # Verify it's valid JSON
        import json
        data = json.loads(report)
        self.assertEqual(data["total_entries"], 3)
        self.assertEqual(data["total_projects"], 2)

    def test_generate_csv_report(self):
        """Test generating a CSV format report."""
        report = self.generator.generate(
            period="daily", format_type="csv"
        )
        lines = report.strip().split("\n")
        # Header row
        self.assertIn("ID", lines[0])
        self.assertIn("Project", lines[0])
        # Data rows (3 entries) + blank line + summary lines (3)
        self.assertGreaterEqual(len(lines), 7)

    def test_generate_html_report(self):
        """Test generating an HTML format report."""
        report = self.generator.generate(
            period="daily", format_type="html"
        )
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("<html", report)
        self.assertIn("</html>", report)
        self.assertIn("project-alpha", report)
        self.assertIn("project-beta", report)
        self.assertIn("inline", report)  # Has inline styles

    def test_generate_markdown_report(self):
        """Test generating a Markdown format report."""
        report = self.generator.generate(
            period="daily", format_type="markdown"
        )
        self.assertIn("# TimeForge Report", report)
        self.assertIn("## Summary", report)
        self.assertIn("## Project Distribution", report)
        self.assertIn("project-alpha", report)
        self.assertIn("|", report)  # Table syntax

    def test_report_filter_by_project(self):
        """Test filtering report by project name."""
        report = self.generator.generate(
            period="daily", format_type="json", project="project-alpha"
        )
        import json
        data = json.loads(report)
        self.assertEqual(data["total_entries"], 2)
        self.assertEqual(data["total_projects"], 1)

    def test_report_date_range(self):
        """Test generating report with custom date range."""
        report = self.generator.generate(
            period="daily",
            format_type="json",
            from_date="2025-01-01",
            to_date="2025-01-31",
        )
        import json
        data = json.loads(report)
        self.assertEqual(data["start_date"], "2025-01-01")
        self.assertEqual(data["end_date"], "2025-01-31")
        self.assertEqual(data["total_entries"], 0)

    def test_report_empty_data(self):
        """Test generating report with no data."""
        empty_storage = Storage(data_dir=tempfile.mkdtemp())
        gen = ReportGenerator(storage=empty_storage)
        report = gen.generate(period="daily", format_type="json")
        import json
        data = json.loads(report)
        self.assertEqual(data["total_entries"], 0)

    def test_report_total_time_calculation(self):
        """Test that total time is correctly calculated."""
        report = self.generator.generate(
            period="daily", format_type="json"
        )
        import json
        data = json.loads(report)
        # 5400 + 7200 + 3600 = 16200 seconds
        self.assertEqual(data["total_time"], 16200.0)

    def test_report_project_percentages(self):
        """Test that project percentages are correctly calculated."""
        report = self.generator.generate(
            period="daily", format_type="json"
        )
        import json
        data = json.loads(report)
        projects = {p["name"]: p["percentage"] for p in data["projects"]}
        # alpha: 12600/16200 = 77.78%, beta: 3600/16200 = 22.22%
        self.assertAlmostEqual(projects["project-alpha"], 77.78, places=1)
        self.assertAlmostEqual(projects["project-beta"], 22.22, places=1)

    def test_invalid_format_raises_error(self):
        """Test that an invalid format raises ValueError."""
        with self.assertRaises(ValueError):
            self.generator.generate(
                period="daily", format_type="xml"
            )

    def test_html_escaping(self):
        """Test that HTML special characters are escaped."""
        self.storage.add_entry(TimeEntry(
            project="test<script>",
            description="<b>alert</b>",
            start_time=datetime.now().isoformat(),
            duration=60.0,
        ))
        report = self.generator.generate(
            period="daily", format_type="html"
        )
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)


if __name__ == "__main__":
    unittest.main()
