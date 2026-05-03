"""Report generation feature for TimeForge.

Generates time tracking reports in multiple formats: JSON, CSV, HTML,
and Markdown. Supports daily, weekly, and monthly aggregation with
project filtering and date range selection.
"""

import csv
import io
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..core.models import TimeEntry
from ..core.storage import Storage
from ..utils.display import Display, Colors


class ReportGenerator:
    """Multi-format report generator for TimeForge data.

    Generates reports from time tracking data in JSON, CSV, HTML, and
    Markdown formats. Supports filtering by project and date range.

    Attributes:
        storage: The Storage engine instance for data access.
        display: The Display utility for terminal output.
    """

    def __init__(self, storage: Optional[Storage] = None):
        """Initialize the ReportGenerator.

        Args:
            storage: Custom Storage instance. Creates default if None.
        """
        self.storage = storage or Storage()
        self.display = Display()

    def generate(
        self,
        period: str = "daily",
        format_type: str = "markdown",
        project: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> str:
        """Generate a report in the specified format.

        Args:
            period: Report period - 'daily', 'weekly', or 'monthly'.
            format_type: Output format - 'json', 'csv', 'html', or 'markdown'.
            project: Filter by project name. None for all projects.
            from_date: Start date in YYYY-MM-DD format.
            to_date: End date in YYYY-MM-DD format.

        Returns:
            The generated report as a string.
        """
        # Determine date range based on period
        if from_date and to_date:
            start_date = from_date
            end_date = to_date
        else:
            start_date, end_date = self._get_period_range(period)

        # Get entries
        entries = self.storage.get_entries_by_date_range(start_date, end_date)

        # Filter by project
        if project:
            entries = [e for e in entries if e.project == project]

        # Sort by start_time ascending
        entries.sort(key=lambda e: e.start_time)

        # Generate report data
        report_data = self._build_report_data(
            entries, start_date, end_date, period
        )

        # Format output
        if format_type == "json":
            return self._format_json(report_data)
        elif format_type == "csv":
            return self._format_csv(entries, report_data)
        elif format_type == "html":
            return self._format_html(report_data, start_date, end_date)
        elif format_type == "markdown":
            return self._format_markdown(report_data, start_date, end_date)
        else:
            raise ValueError(f"Unknown format: {format_type}")

    def _get_period_range(self, period: str) -> tuple:
        """Calculate date range for a report period.

        Args:
            period: 'daily', 'weekly', or 'monthly'.

        Returns:
            Tuple of (start_date, end_date) as YYYY-MM-DD strings.
        """
        today = datetime.now()

        if period == "daily":
            start = today
            end = today
        elif period == "weekly":
            # Start from Monday of current week
            start = today - timedelta(days=today.weekday())
            end = today
        elif period == "monthly":
            start = today.replace(day=1)
            end = today
        else:
            start = today
            end = today

        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    def _build_report_data(
        self,
        entries: List[TimeEntry],
        start_date: str,
        end_date: str,
        period: str,
    ) -> Dict[str, Any]:
        """Build structured report data from time entries.

        Args:
            entries: List of TimeEntry objects.
            start_date: Report start date.
            end_date: Report end date.
            period: Report period type.

        Returns:
            Dictionary containing all report data.
        """
        # Calculate totals
        total_time = sum(e.compute_duration() for e in entries)

        # Group by project
        project_data: Dict[str, Dict[str, Any]] = {}
        for entry in entries:
            name = entry.project
            if name not in project_data:
                project_data[name] = {
                    "name": name,
                    "entries": [],
                    "total_time": 0.0,
                    "entry_count": 0,
                }
            duration = entry.compute_duration()
            project_data[name]["entries"].append(entry)
            project_data[name]["total_time"] += duration
            project_data[name]["entry_count"] += 1

        # Calculate percentages
        projects_list = list(project_data.values())
        for proj in projects_list:
            if total_time > 0:
                proj["percentage"] = (proj["total_time"] / total_time) * 100
            else:
                proj["percentage"] = 0.0

        # Sort by total time descending
        projects_list.sort(key=lambda p: p["total_time"], reverse=True)

        # Group by date
        daily_data: Dict[str, Dict[str, Any]] = {}
        for entry in entries:
            date_key = entry.start_time[:10]
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "entries": [],
                    "total_time": 0.0,
                    "entry_count": 0,
                }
            duration = entry.compute_duration()
            daily_data[date_key]["entries"].append(entry)
            daily_data[date_key]["total_time"] += duration
            daily_data[date_key]["entry_count"] += 1

        daily_list = sorted(
            daily_data.values(), key=lambda d: d["date"], reverse=True
        )

        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().isoformat(),
            "total_time": total_time,
            "total_entries": len(entries),
            "total_projects": len(projects_list),
            "projects": projects_list,
            "daily": daily_list,
            "entries": [
                {
                    "id": e.id,
                    "project": e.project,
                    "description": e.description,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "duration": e.compute_duration(),
                }
                for e in entries
            ],
        }

    def _format_json(self, data: Dict[str, Any]) -> str:
        """Format report data as JSON.

        Args:
            data: Report data dictionary.

        Returns:
            JSON formatted string.
        """
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    def _format_csv(
        self, entries: List[TimeEntry], data: Dict[str, Any]
    ) -> str:
        """Format report data as CSV.

        Args:
            entries: List of TimeEntry objects.
            data: Report data dictionary.

        Returns:
            CSV formatted string.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "ID", "Project", "Description", "Start Time",
            "End Time", "Duration (seconds)", "Duration",
        ])

        # Data rows
        for entry in entries:
            duration = entry.compute_duration()
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_str = f"{hours}h {minutes}m {seconds}s"

            writer.writerow([
                entry.id,
                entry.project,
                entry.description,
                entry.start_time,
                entry.end_time or "",
                f"{duration:.0f}",
                duration_str,
            ])

        # Summary
        writer.writerow([])
        writer.writerow(["Total Time", "", "", "", "", f"{data['total_time']:.0f}", ""])
        writer.writerow(["Total Entries", str(data["total_entries"])])
        writer.writerow(["Total Projects", str(data["total_projects"])])

        return output.getvalue()

    def _format_html(
        self, data: Dict[str, Any], start_date: str, end_date: str
    ) -> str:
        """Format report data as HTML with inline CSS styling.

        Args:
            data: Report data dictionary.
            start_date: Report start date.
            end_date: Report end date.

        Returns:
            HTML formatted string.
        """
        total_hours = data["total_time"] / 3600

        # Build project rows
        project_rows = ""
        for proj in data["projects"]:
            proj_hours = proj["total_time"] / 3600
            pct = proj["percentage"]
            project_rows += f"""
            <tr>
                <td>{self._html_escape(proj['name'])}</td>
                <td>{proj['entry_count']}</td>
                <td>{proj_hours:.2f}h</td>
                <td>
                    <div class="bar-container">
                        <div class="bar" style="width: {pct:.1f}%"></div>
                    </div>
                    {pct:.1f}%
                </td>
            </tr>"""

        # Build entry rows
        entry_rows = ""
        for entry in data["entries"]:
            dur = entry["duration"]
            hours = int(dur // 3600)
            minutes = int((dur % 3600) // 60)
            seconds = int(dur % 60)
            entry_rows += f"""
            <tr>
                <td>{entry['id']}</td>
                <td>{self._html_escape(entry['project'])}</td>
                <td>{self._html_escape(entry['description'] or '-')}</td>
                <td>{entry['start_time'][:16]}</td>
                <td>{entry['end_time'][:16] if entry['end_time'] else '-'}</td>
                <td>{hours}h {minutes}m {seconds}s</td>
            </tr>"""

        # Build daily rows
        daily_rows = ""
        for day in data["daily"]:
            day_hours = day["total_time"] / 3600
            daily_rows += f"""
            <tr>
                <td>{day['date']}</td>
                <td>{day['entry_count']}</td>
                <td>{day_hours:.2f}h</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TimeForge Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #2c3e50;
            margin: 30px 0 15px;
            font-size: 1.3em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card .label {{
            color: #7f8c8d;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .summary-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        th {{
            background: #2c3e50;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .bar-container {{
            background: #ecf0f1;
            border-radius: 4px;
            height: 20px;
            width: 100%;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }}
        .bar {{
            background: linear-gradient(90deg, #3498db, #2ecc71);
            height: 100%;
            border-radius: 4px;
            min-width: 2px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.85em;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>TimeForge Report</h1>
        <p>Period: {start_date} to {end_date} | Generated: {data['generated_at'][:19]}</p>

        <div class="summary">
            <div class="summary-card">
                <div class="label">Total Time</div>
                <div class="value">{total_hours:.2f}h</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Entries</div>
                <div class="value">{data['total_entries']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Projects</div>
                <div class="value">{data['total_projects']}</div>
            </div>
        </div>

        <h2>Project Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Project</th>
                    <th>Entries</th>
                    <th>Time</th>
                    <th>Distribution</th>
                </tr>
            </thead>
            <tbody>
                {project_rows}
            </tbody>
        </table>

        <h2>Daily Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Entries</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                {daily_rows}
            </tbody>
        </table>

        <h2>Time Entries</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Project</th>
                    <th>Description</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                {entry_rows}
            </tbody>
        </table>

        <div class="footer">
            Generated by TimeForge
        </div>
    </div>
</body>
</html>"""
        return html

    def _format_markdown(
        self, data: Dict[str, Any], start_date: str, end_date: str
    ) -> str:
        """Format report data as Markdown with tables.

        Args:
            data: Report data dictionary.
            start_date: Report start date.
            end_date: Report end date.

        Returns:
            Markdown formatted string.
        """
        total_hours = data["total_time"] / 3600

        lines = [
            f"# TimeForge Report",
            f"",
            f"**Period:** {start_date} to {end_date}",
            f"**Generated:** {data['generated_at'][:19]}",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Time | {total_hours:.2f}h |",
            f"| Total Entries | {data['total_entries']} |",
            f"| Projects | {data['total_projects']} |",
            f"",
        ]

        # Project distribution
        if data["projects"]:
            lines.extend([
                "## Project Distribution",
                "",
                "| Project | Entries | Time | Percentage |",
                "|---------|---------|------|------------|",
            ])
            for proj in data["projects"]:
                proj_hours = proj["total_time"] / 3600
                lines.append(
                    f"| {proj['name']} | {proj['entry_count']} | "
                    f"{proj_hours:.2f}h | {proj['percentage']:.1f}% |"
                )
            lines.append("")

        # Daily summary
        if data["daily"]:
            lines.extend([
                "## Daily Summary",
                "",
                "| Date | Entries | Time |",
                "|------|---------|------|",
            ])
            for day in data["daily"]:
                day_hours = day["total_time"] / 3600
                lines.append(
                    f"| {day['date']} | {day['entry_count']} | "
                    f"{day_hours:.2f}h |"
                )
            lines.append("")

        # Detailed entries
        if data["entries"]:
            lines.extend([
                "## Time Entries",
                "",
                "| ID | Project | Description | Start | End | Duration |",
                "|----|---------|-------------|-------|-----|----------|",
            ])
            for entry in data["entries"]:
                dur = entry["duration"]
                hours = int(dur // 3600)
                minutes = int((dur % 3600) // 60)
                desc = (entry["description"] or "-")[:40]
                start = entry["start_time"][:16]
                end = entry["end_time"][:16] if entry["end_time"] else "-"
                lines.append(
                    f"| {entry['id']} | {entry['project']} | "
                    f"{desc} | {start} | {end} | "
                    f"{hours}h {minutes}m |"
                )
            lines.append("")

        lines.extend([
            "---",
            "*Generated by TimeForge*",
        ])

        return "\n".join(lines)

    @staticmethod
    def _html_escape(text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: The text to escape.

        Returns:
            HTML-safe string.
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
