"""Configuration management for TimeForge.

Handles loading, saving, and accessing user configuration stored in
~/.timeforge/config.json. Provides sensible defaults for all settings.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for TimeForge.

    Manages user preferences and application settings. Configuration is
    stored as JSON in ~/.timeforge/config.json.

    Attributes:
        config_dir: Path to the TimeForge configuration directory.
        config_file: Path to the configuration JSON file.
        _config: In-memory configuration dictionary.
    """

    DEFAULT_CONFIG = {
        "work_hours_per_day": 8.0,
        "pomodoro_work_minutes": 25,
        "pomodoro_short_break_minutes": 5,
        "pomodoro_long_break_minutes": 15,
        "pomodoro_sessions_before_long_break": 4,
        "idle_reminder_minutes": 5,
        "default_project": None,
        "editor": None,
        "report_format": "markdown",
        "theme": "default",
        "auto_git_link": False,
        "date_format": "%Y-%m-%d",
        "time_format": "%H:%M",
    }

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the Config manager.

        Loads existing configuration or creates default configuration.

        Args:
            config_dir: Custom configuration directory. Defaults to ~/.timeforge.
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".timeforge"

        self.config_file = self.config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file, merging with defaults."""
        self._config = dict(self.DEFAULT_CONFIG)
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                self._config.update(user_config)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults on error

    def _save(self) -> None:
        """Save current configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key name.
            default: Default value if key is not found.

        Returns:
            The configuration value, or default if not found.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and persist to file.

        Args:
            key: Configuration key name.
            value: Value to set.
        """
        self._config[key] = value
        self._save()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.

        Returns:
            Complete configuration dictionary.
        """
        return dict(self._config)

    def reset(self) -> None:
        """Reset all configuration to default values."""
        self._config = dict(self.DEFAULT_CONFIG)
        self._save()

    def reset_key(self, key: str) -> None:
        """Reset a single configuration key to its default value.

        Args:
            key: Configuration key name to reset.
        """
        if key in self.DEFAULT_CONFIG:
            self._config[key] = self.DEFAULT_CONFIG[key]
            self._save()

    # ── Convenience properties ────────────────────────────────────────

    @property
    def work_hours_per_day(self) -> float:
        """Get the configured daily work hours target."""
        return self.get("work_hours_per_day", 8.0)

    @work_hours_per_day.setter
    def work_hours_per_day(self, value: float) -> None:
        """Set the daily work hours target."""
        self.set("work_hours_per_day", value)

    @property
    def pomodoro_work_minutes(self) -> int:
        """Get the configured pomodoro work duration in minutes."""
        return self.get("pomodoro_work_minutes", 25)

    @pomodoro_work_minutes.setter
    def pomodoro_work_minutes(self, value: int) -> None:
        """Set the pomodoro work duration in minutes."""
        self.set("pomodoro_work_minutes", value)

    @property
    def pomodoro_short_break_minutes(self) -> int:
        """Get the configured short break duration in minutes."""
        return self.get("pomodoro_short_break_minutes", 5)

    @pomodoro_short_break_minutes.setter
    def pomodoro_short_break_minutes(self, value: int) -> None:
        """Set the short break duration in minutes."""
        self.set("pomodoro_short_break_minutes", value)

    @property
    def pomodoro_long_break_minutes(self) -> int:
        """Get the configured long break duration in minutes."""
        return self.get("pomodoro_long_break_minutes", 15)

    @pomodoro_long_break_minutes.setter
    def pomodoro_long_break_minutes(self, value: int) -> None:
        """Set the long break duration in minutes."""
        self.set("pomodoro_long_break_minutes", value)

    @property
    def pomodoro_sessions_before_long_break(self) -> int:
        """Get the number of pomodoro sessions before a long break."""
        return self.get("pomodoro_sessions_before_long_break", 4)

    @pomodoro_sessions_before_long_break.setter
    def pomodoro_sessions_before_long_break(self, value: int) -> None:
        """Set the number of sessions before a long break."""
        self.set("pomodoro_sessions_before_long_break", value)

    @property
    def idle_reminder_minutes(self) -> int:
        """Get the idle reminder interval in minutes."""
        return self.get("idle_reminder_minutes", 5)

    @idle_reminder_minutes.setter
    def idle_reminder_minutes(self, value: int) -> None:
        """Set the idle reminder interval in minutes."""
        self.set("idle_reminder_minutes", value)

    @property
    def default_project(self) -> Optional[str]:
        """Get the default project name."""
        return self.get("default_project")

    @default_project.setter
    def default_project(self, value: Optional[str]) -> None:
        """Set the default project name."""
        self.set("default_project", value)

    @property
    def report_format(self) -> str:
        """Get the default report format."""
        return self.get("report_format", "markdown")

    @report_format.setter
    def report_format(self, value: str) -> None:
        """Set the default report format."""
        self.set("report_format", value)

    @property
    def auto_git_link(self) -> bool:
        """Get whether auto git linking is enabled."""
        return self.get("auto_git_link", False)

    @auto_git_link.setter
    def auto_git_link(self, value: bool) -> None:
        """Set whether auto git linking is enabled."""
        self.set("auto_git_link", value)
