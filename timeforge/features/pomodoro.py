"""Pomodoro timer feature for TimeForge.

Implements the Pomodoro Technique with configurable work/break durations,
terminal progress bar display, and completion notifications.
"""

import json
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.display import Display, Colors
from ..utils.config import Config


class PomodoroTimer:
    """Pomodoro Technique timer with terminal interface.

    Supports configurable work and break durations, tracks completed
    sessions, and provides visual progress feedback in the terminal.

    Attributes:
        config: The Config instance for timer settings.
        display: The Display utility for terminal output.
        state_file: Path to the pomodoro state file.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the PomodoroTimer.

        Args:
            config: Custom Config instance. Creates default if None.
        """
        self.config = config or Config()
        self.display = Display()
        self.state_file = Path.home() / ".timeforge" / "pomodoro_state.json"
        self._running = False
        self._state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load pomodoro state from file.

        Returns:
            State dictionary with session counts and timer info.
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "completed_sessions": 0,
            "total_sessions_today": 0,
            "last_date": None,
            "is_running": False,
            "is_break": False,
            "start_time": None,
            "duration_seconds": 0,
        }

    def _save_state(self) -> None:
        """Save pomodoro state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
        except IOError:
            pass

    def _reset_daily_count(self) -> None:
        """Reset the daily session count if it's a new day."""
        today = datetime.now().strftime("%Y-%m-%d")
        if self._state.get("last_date") != today:
            self._state["total_sessions_today"] = 0
            self._state["last_date"] = today

    def start(self, duration_minutes: Optional[int] = None) -> None:
        """Start a pomodoro work session.

        Args:
            duration_minutes: Custom work duration in minutes.
                Defaults to configured value (25 minutes).
        """
        if self._state.get("is_running"):
            self.display.warning("A pomodoro session is already running!")
            self.status()
            return

        work_minutes = duration_minutes or self.config.pomodoro_work_minutes
        duration_seconds = work_minutes * 60

        self._state["is_running"] = True
        self._state["is_break"] = False
        self._state["start_time"] = datetime.now().isoformat()
        self._state["duration_seconds"] = duration_seconds
        self._save_state()

        self._reset_daily_count()

        self.display.header("Pomodoro Timer")
        self.display.info(
            f"Work session: {Colors.bold(str(work_minutes))} minutes"
        )
        self.display.info("Press Ctrl+C to stop early.")
        self._print_session_count()
        self._print()

        self._run_timer(duration_seconds, is_break=False)

    def start_break(self, is_long: bool = False) -> None:
        """Start a break session.

        Args:
            is_long: Whether this is a long break (15 min) vs short (5 min).
        """
        if self._state.get("is_running"):
            self.display.warning("A session is already running!")
            return

        if is_long:
            break_minutes = self.config.pomodoro_long_break_minutes
            break_type = "Long break"
        else:
            break_minutes = self.config.pomodoro_short_break_minutes
            break_type = "Short break"

        duration_seconds = break_minutes * 60

        self._state["is_running"] = True
        self._state["is_break"] = True
        self._state["start_time"] = datetime.now().isoformat()
        self._state["duration_seconds"] = duration_seconds
        self._save_state()

        self.display.header("Pomodoro Break")
        self.display.info(
            f"{break_type}: {Colors.bold(str(break_minutes))} minutes"
        )
        self.display.info("Press Ctrl+C to stop early.")
        self._print()

        self._run_timer(duration_seconds, is_break=True)

    def stop(self) -> None:
        """Stop the current pomodoro session."""
        if not self._state.get("is_running"):
            self.display.warning("No pomodoro session is running.")
            return

        self._state["is_running"] = False
        self._state["is_break"] = False
        self._save_state()

        self.display.clear_line()
        self.display.warning("Pomodoro session stopped.")

    def status(self) -> None:
        """Display the current pomodoro status."""
        if not self._state.get("is_running"):
            self.display.info("No pomodoro session is running.")
            self._print_session_count()
            return

        start_time = datetime.fromisoformat(self._state["start_time"])
        elapsed = (datetime.now() - start_time).total_seconds()
        total = self._state["duration_seconds"]
        remaining = max(0, total - elapsed)

        session_type = "Break" if self._state.get("is_break") else "Work"
        self.display.header(f"Pomodoro Status - {session_type}")

        # Progress bar
        progress = min(elapsed / total, 1.0) if total > 0 else 0
        bar_str = self.display.progress_bar(
            elapsed, total, label="Progress"
        )
        self._print(f"  {bar_str}")

        # Time info
        remaining_min = int(remaining // 60)
        remaining_sec = int(remaining % 60)
        self._print(
            f"  Time remaining: {Colors.bold(f'{remaining_min:02d}:{remaining_sec:02d}')}"
        )

        self._print_session_count()

    def show_config(self) -> None:
        """Display current pomodoro configuration."""
        self.display.header("Pomodoro Configuration")
        rows = [
            ["Work duration", f"{self.config.pomodoro_work_minutes} min"],
            ["Short break", f"{self.config.pomodoro_short_break_minutes} min"],
            ["Long break", f"{self.config.pomodoro_long_break_minutes} min"],
            [
                "Sessions before long break",
                str(self.config.pomodoro_sessions_before_long_break),
            ],
        ]
        self.display.table(["Setting", "Value"], rows)

    def _run_timer(self, duration_seconds: int, is_break: bool) -> None:
        """Run the countdown timer with progress display.

        Args:
            duration_seconds: Total duration of the timer in seconds.
            is_break: Whether this is a break timer.
        """
        self._running = True
        start_time = time.time()

        try:
            while self._running:
                elapsed = time.time() - start_time
                remaining = max(0, duration_seconds - elapsed)

                if remaining <= 0:
                    break

                # Update progress bar
                progress = elapsed / duration_seconds
                remaining_min = int(remaining // 60)
                remaining_sec = int(remaining % 60)

                bar = self.display.progress_bar(
                    elapsed, duration_seconds, width=40
                )
                sys.stdout.write(
                    f"\r  {bar}  "
                    f"{remaining_min:02d}:{remaining_sec:02d}"
                )
                sys.stdout.flush()

                time.sleep(1)

            # Timer completed
            self.display.clear_line()

            if self._running:
                if is_break:
                    self.display.success("Break is over! Time to work!")
                else:
                    self._on_work_complete()
            else:
                # Stopped early
                pass

        except KeyboardInterrupt:
            self.display.clear_line()
            self.display.warning("Timer stopped by user.")

        finally:
            self._running = False
            self._state["is_running"] = False
            self._state["is_break"] = False
            self._save_state()

    def _on_work_complete(self) -> None:
        """Handle work session completion.

        Increments session count and suggests appropriate break.
        """
        self._state["completed_sessions"] += 1
        self._state["total_sessions_today"] += 1
        self._save_state()

        # Completion animation
        self.display.completion_animation("Pomodoro Complete!")

        self._print_session_count()

        # Suggest break
        sessions = self._state["total_sessions_today"]
        threshold = self.config.pomodoro_sessions_before_long_break

        if sessions % threshold == 0:
            self.display.info(
                f"{Colors.yellow('Great work!')} "
                f"Time for a {Colors.bold(str(self.config.pomodoro_long_break_minutes))} "
                f"minute long break."
            )
        else:
            self.display.info(
                f"Time for a {Colors.bold(str(self.config.pomodoro_short_break_minutes))} "
                f"minute short break."
            )

    def _print_session_count(self) -> None:
        """Print the current session count."""
        total = self._state.get("completed_sessions", 0)
        today = self._state.get("total_sessions_today", 0)
        self._print(
            f"  Sessions today: {Colors.bold(str(today))} | "
            f"Total: {Colors.bold(str(total))}"
        )

    def _print(self, text: str = "") -> None:
        """Print text to stdout.

        Args:
            text: The text to print.
        """
        print(text)
