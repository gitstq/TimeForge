"""Productivity analytics engine for TimeForge.

Provides comprehensive analysis of time tracking data including work
patterns, project distribution, streaks, efficiency scores, and
intelligent suggestions.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..core.models import TimeEntry
from ..core.storage import Storage
from ..utils.display import Display, Colors


class AnalyticsEngine:
    """Productivity analytics engine for TimeForge.

    Analyzes time tracking data to provide insights about work patterns,
    productivity trends, and actionable suggestions.

    Attributes:
        storage: The Storage engine instance for data access.
        display: The Display utility for terminal output.
    """

    def __init__(self, storage: Optional[Storage] = None):
        """Initialize the AnalyticsEngine.

        Args:
            storage: Custom Storage instance. Creates default if None.
        """
        self.storage = storage or Storage()
        self.display = Display()

    def analyze(self, days: int = 30) -> Dict[str, Any]:
        """Run a comprehensive productivity analysis.

        Args:
            days: Number of days to analyze (default 30).

        Returns:
            Dictionary containing all analysis results.
        """
        entries = self._get_recent_entries(days)

        if not entries:
            self.display.warning(
                f"No time entries found in the last {days} days."
            )
            return {}

        analysis: Dict[str, Any] = {
            "period_days": days,
            "total_entries": len(entries),
            "total_time": 0.0,
            "daily_stats": {},
            "project_distribution": {},
            "hourly_distribution": defaultdict(float),
            "weekday_distribution": defaultdict(float),
            "streak": 0,
            "longest_streak": 0,
            "efficiency_score": 0.0,
            "suggestions": [],
        }

        # Calculate totals and distributions
        total_time = 0.0
        project_times: Dict[str, float] = defaultdict(float)
        project_counts: Dict[str, int] = defaultdict(int)
        daily_times: Dict[str, float] = defaultdict(float)
        daily_counts: Dict[str, int] = defaultdict(int)
        hourly_times: Dict[int, float] = defaultdict(float)
        weekday_times: Dict[int, float] = defaultdict(float)

        for entry in entries:
            duration = entry.compute_duration()
            total_time += duration

            # Project distribution
            project_times[entry.project] += duration
            project_counts[entry.project] += 1

            # Daily stats
            date_key = entry.start_time[:10]
            daily_times[date_key] += duration
            daily_counts[date_key] += 1

            # Hourly distribution (hour of day)
            try:
                hour = datetime.fromisoformat(entry.start_time).hour
                hourly_times[hour] += duration
            except (ValueError, TypeError):
                pass

            # Weekday distribution
            try:
                weekday = datetime.fromisoformat(entry.start_time).weekday()
                weekday_times[weekday] += duration
            except (ValueError, TypeError):
                pass

        analysis["total_time"] = total_time

        # Build daily stats
        for date_key in sorted(daily_times.keys()):
            analysis["daily_stats"][date_key] = {
                "total_time": daily_times[date_key],
                "entry_count": daily_counts[date_key],
            }

        # Build project distribution
        project_list = []
        for name, time_val in sorted(
            project_times.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (time_val / total_time * 100) if total_time > 0 else 0
            project_list.append({
                "name": name,
                "total_time": time_val,
                "entry_count": project_counts[name],
                "percentage": percentage,
            })
        analysis["project_distribution"] = project_list

        # Hourly distribution
        analysis["hourly_distribution"] = dict(hourly_times)

        # Weekday distribution
        weekday_names = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday",
        ]
        weekday_list = []
        for day_num in range(7):
            time_val = weekday_times.get(day_num, 0.0)
            weekday_list.append({
                "day": weekday_names[day_num],
                "day_num": day_num,
                "total_time": time_val,
                "percentage": (
                    time_val / total_time * 100 if total_time > 0 else 0
                ),
            })
        analysis["weekday_distribution"] = weekday_list

        # Calculate streaks
        streak, longest_streak = self._calculate_streaks(daily_times)
        analysis["streak"] = streak
        analysis["longest_streak"] = longest_streak

        # Calculate efficiency score
        analysis["efficiency_score"] = self._calculate_efficiency(
            daily_times, total_time, days
        )

        # Generate suggestions
        analysis["suggestions"] = self._generate_suggestions(
            analysis, hourly_times, weekday_times, project_times
        )

        return analysis

    def display_analysis(self, days: int = 30) -> None:
        """Run and display a comprehensive analysis.

        Args:
            days: Number of days to analyze.
        """
        analysis = self.analyze(days)
        if not analysis:
            return

        self.display.header(f"Productivity Analysis (Last {days} Days)")

        # Summary
        total_hours = analysis["total_time"] / 3600
        avg_daily = total_hours / max(days, 1)
        self.display.info(
            f"Total tracked: {Colors.bold(f'{total_hours:.1f}h')} "
            f"({analysis['total_entries']} entries)"
        )
        self.display.info(
            f"Daily average: {Colors.bold(f'{avg_daily:.1f}h')}"
        )
        self.display.info(
            f"Current streak: {Colors.bold(str(analysis['streak']))} days "
            f"(longest: {analysis['longest_streak']} days)"
        )
        self.display.info(
            f"Efficiency score: {self._score_display(analysis['efficiency_score'])}"
        )
        self._print()

        # Project distribution chart
        if analysis["project_distribution"]:
            self.display.header("Project Distribution")
            chart_data = [
                (p["name"], p["percentage"])
                for p in analysis["project_distribution"]
            ]
            self.display.bar_chart(
                chart_data, title="Time by Project (%)"
            )

            # Project table
            rows = []
            for p in analysis["project_distribution"]:
                hours = p["total_time"] / 3600
                rows.append([
                    p["name"],
                    str(p["entry_count"]),
                    f"{hours:.1f}h",
                    f"{p['percentage']:.1f}%",
                ])
            self.display.table(
                ["Project", "Entries", "Time", "Share"], rows
            )

        # Hourly distribution chart
        if analysis["hourly_distribution"]:
            self.display.header("Work Hours Distribution")
            hourly = analysis["hourly_distribution"]
            chart_data = []
            for hour in range(24):
                if hour in hourly:
                    chart_data.append((f"{hour:02d}:00", hourly[hour] / 3600))
            if chart_data:
                self.display.bar_chart(
                    chart_data, title="Hours by Time of Day"
                )

        # Weekday distribution
        if analysis["weekday_distribution"]:
            self.display.header("Weekday Distribution")
            rows = []
            for wd in analysis["weekday_distribution"]:
                hours = wd["total_time"] / 3600
                rows.append([
                    wd["day"],
                    f"{hours:.1f}h",
                    f"{wd['percentage']:.1f}%",
                ])
            self.display.table(
                ["Day", "Time", "Share"], rows
            )

        # Suggestions
        if analysis["suggestions"]:
            self.display.header("Suggestions")
            for suggestion in analysis["suggestions"]:
                self.display.info(f"  {Colors.cyan('-')} {suggestion}")
            self._print()

    def _get_recent_entries(self, days: int) -> List[TimeEntry]:
        """Get time entries from the last N days.

        Args:
            days: Number of days to look back.

        Returns:
            List of TimeEntry objects from the specified period.
        """
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        return self.storage.get_entries_by_date_range(cutoff, today)

    def _calculate_streaks(
        self, daily_times: Dict[str, float]
    ) -> Tuple[int, int]:
        """Calculate current and longest work streaks.

        Args:
            daily_times: Dictionary mapping date strings to total seconds.

        Returns:
            Tuple of (current_streak, longest_streak).
        """
        if not daily_times:
            return 0, 0

        sorted_dates = sorted(daily_times.keys())
        current_streak = 0
        longest_streak = 0
        temp_streak = 1

        # Check if today or yesterday has entries (for current streak)
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (
            datetime.now() - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        if today in daily_times:
            current_streak = 1
        elif yesterday in daily_times:
            current_streak = 1
        else:
            return 0, 0

        # Calculate current streak backwards from today/yesterday
        check_date = datetime.now()
        if today not in daily_times:
            check_date -= timedelta(days=1)

        for i in range(1, 365):
            prev_date = (check_date - timedelta(days=i)).strftime("%Y-%m-%d")
            if prev_date in daily_times:
                current_streak += 1
            else:
                break

        # Calculate longest streak
        for i in range(1, len(sorted_dates)):
            prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
            curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
            diff = (curr - prev).days
            if diff == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        longest_streak = max(longest_streak, temp_streak)

        return current_streak, longest_streak

    def _calculate_efficiency(
        self,
        daily_times: Dict[str, float],
        total_time: float,
        days: int,
    ) -> float:
        """Calculate a productivity efficiency score (0-100).

        Based on:
        - Consistency (how many days had tracked time)
        - Regularity (standard deviation of daily hours)
        - Volume (total hours relative to target)

        Args:
            daily_times: Dictionary mapping date strings to total seconds.
            total_time: Total tracked time in seconds.
            days: Number of days in the analysis period.

        Returns:
            Efficiency score from 0 to 100.
        """
        if not daily_times or total_time <= 0:
            return 0.0

        # Consistency score (0-40): percentage of days with activity
        active_days = len(daily_times)
        consistency = min(active_days / max(days, 1), 1.0) * 40

        # Regularity score (0-30): based on standard deviation
        daily_hours = [t / 3600 for t in daily_times.values()]
        if len(daily_hours) > 1:
            mean = sum(daily_hours) / len(daily_hours)
            variance = sum((h - mean) ** 2 for h in daily_hours) / len(daily_hours)
            std_dev = variance ** 0.5
            # Lower std_dev relative to mean = more regular = higher score
            if mean > 0:
                cv = std_dev / mean  # coefficient of variation
                regularity = max(0, 30 * (1 - min(cv, 2.0) / 2.0))
            else:
                regularity = 0
        else:
            regularity = 15  # Neutral score for single day

        # Volume score (0-30): based on average daily hours
        avg_daily_hours = total_time / 3600 / max(days, 1)
        # Assume 8h/day is optimal, score scales linearly up to that
        volume = min(avg_daily_hours / 8.0, 1.0) * 30

        return round(consistency + regularity + volume, 1)

    def _generate_suggestions(
        self,
        analysis: Dict[str, Any],
        hourly_times: Dict[int, float],
        weekday_times: Dict[int, float],
        project_times: Dict[str, float],
    ) -> List[str]:
        """Generate intelligent productivity suggestions.

        Args:
            analysis: The complete analysis dictionary.
            hourly_times: Dictionary mapping hours to total seconds.
            weekday_times: Dictionary mapping weekday numbers to seconds.
            project_times: Dictionary mapping project names to seconds.

        Returns:
            List of suggestion strings.
        """
        suggestions = []
        total_time = analysis["total_time"]

        # Find peak productivity hour
        if hourly_times:
            peak_hour = max(hourly_times, key=hourly_times.get)
            peak_minutes = hourly_times[peak_hour] / 60
            suggestions.append(
                f"You are most productive around {peak_hour:02d}:00 "
                f"(avg {peak_minutes:.0f} min tracked at that hour)."
            )

        # Find most productive day
        if weekday_times:
            peak_day_num = max(weekday_times, key=weekday_times.get)
            weekday_names = [
                "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday",
            ]
            suggestions.append(
                f"Your most productive day is {weekday_names[peak_day_num]}."
            )

        # Check for low-activity days
        daily_stats = analysis.get("daily_stats", {})
        if daily_stats:
            avg_time = total_time / max(len(daily_stats), 1)
            low_days = [
                date for date, stats in daily_stats.items()
                if stats["total_time"] < avg_time * 0.3
            ]
            if len(low_days) > len(daily_stats) * 0.5:
                suggestions.append(
                    "Your productivity varies significantly between days. "
                    "Try to maintain a more consistent schedule."
                )

        # Check project focus
        if project_times and len(project_times) > 1:
            sorted_projects = sorted(
                project_times.items(), key=lambda x: x[1], reverse=True
            )
            top_project = sorted_projects[0]
            top_pct = top_project[1] / total_time * 100 if total_time > 0 else 0
            if top_pct > 80:
                suggestions.append(
                    f"You spend {top_pct:.0f}% of your time on "
                    f"'{top_project[0]}'. Consider diversifying your focus."
                )

        # Streak suggestion
        if analysis["streak"] == 0:
            suggestions.append(
                "Start building a daily tracking habit - consistency "
                "leads to better productivity insights."
            )
        elif analysis["streak"] >= 7:
            suggestions.append(
                f"Great streak of {analysis['streak']} days! "
                "Keep up the consistent tracking."
            )

        # Efficiency-based suggestions
        score = analysis["efficiency_score"]
        if score < 30:
            suggestions.append(
                "Your efficiency score is low. Try setting regular "
                "work hours and minimizing context switching."
            )
        elif score >= 70:
            suggestions.append(
                "Excellent work patterns! Your efficiency score is high."
            )

        return suggestions

    def _score_display(self, score: float) -> str:
        """Format an efficiency score with color coding.

        Args:
            score: Efficiency score from 0 to 100.

        Returns:
            Color-coded score string.
        """
        if score >= 70:
            color = Colors.green
        elif score >= 40:
            color = Colors.yellow
        else:
            color = Colors.red
        return color(f"{score:.1f}/100")

    def _print(self, text: str = "") -> None:
        """Print text to stdout.

        Args:
            text: The text to print.
        """
        print(text)
