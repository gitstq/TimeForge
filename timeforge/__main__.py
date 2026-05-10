"""
TimeForge - 终端时间管理工具
"""

__version__ = "1.0.0"
__author__ = "TimeForge Team"
__description__ = "A powerful terminal time management tool with countdown, stopwatch, and pomodoro features"

from .core import TimeForge, TimerConfig, TimerType, TimerState
from .timer import CountdownTimer, StopwatchTimer, PomodoroTimer
from .display import TimerDisplay
from .sound import SoundManager
from .stats import StatsManager

__all__ = [
    "TimeForge",
    "TimerConfig", 
    "TimerType",
    "TimerState",
    "CountdownTimer",
    "StopwatchTimer",
    "PomodoroTimer",
    "TimerDisplay",
    "SoundManager",
    "StatsManager",
]
