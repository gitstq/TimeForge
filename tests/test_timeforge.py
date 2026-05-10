#!/usr/bin/env python3
"""
TimeForge 单元测试
"""

import pytest
import time
from datetime import datetime

from timeforge.core import (
    TimeFormatter, TimerConfig, TimerState, TimerType,
    TimerSession, BaseTimer
)
from timeforge.timer import CountdownTimer, StopwatchTimer, PomodoroTimer


class TestTimeFormatter:
    """时间格式化测试"""
    
    def test_format_seconds_simple(self):
        """测试简单秒数格式化"""
        assert TimeFormatter.format_seconds(0) == "00:00"
        assert TimeFormatter.format_seconds(30) == "00:30"
        assert TimeFormatter.format_seconds(60) == "01:00"
        assert TimeFormatter.format_seconds(90) == "01:30"
        assert TimeFormatter.format_seconds(3600) == "01:00:00"
    
    def test_format_seconds_negative(self):
        """测试负数秒数"""
        assert TimeFormatter.format_seconds(-10) == "00:00"
    
    def test_parse_time_input_seconds(self):
        """测试解析秒数"""
        assert TimeFormatter.parse_time_input("30") == 30
        assert TimeFormatter.parse_time_input("90") == 90
        assert TimeFormatter.parse_time_input("30s") == 30
        assert TimeFormatter.parse_time_input("90s") == 90
    
    def test_parse_time_input_minutes(self):
        """测试解析分钟"""
        assert TimeFormatter.parse_time_input("5m") == 300
        assert TimeFormatter.parse_time_input("10m") == 600
        assert TimeFormatter.parse_time_input("1.5m") == 90
    
    def test_parse_time_input_hours(self):
        """测试解析小时"""
        assert TimeFormatter.parse_time_input("1h") == 3600
        assert TimeFormatter.parse_time_input("2h") == 7200
        assert TimeFormatter.parse_time_input("1.5h") == 5400
    
    def test_parse_time_input_combined(self):
        """测试解析组合时间"""
        assert TimeFormatter.parse_time_input("1h30m") == 5400
        assert TimeFormatter.parse_time_input("1h30m30s") == 5430
    
    def test_parse_time_input_colon(self):
        """测试冒号分隔格式"""
        assert TimeFormatter.parse_time_input("5:00") == 300
        assert TimeFormatter.parse_time_input("1:30:00") == 5400
        assert TimeFormatter.parse_time_input("1:30:30") == 5430


class TestTimerConfig:
    """计时器配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = TimerConfig()
        assert config.work_duration == 25
        assert config.short_break == 5
        assert config.long_break == 15
        assert config.sessions_before_long == 4
        assert config.sound_enabled == True
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = TimerConfig(
            work_duration=30,
            short_break=10,
            long_break=20,
            sound_enabled=False
        )
        assert config.work_duration == 30
        assert config.short_break == 10
        assert config.long_break == 20
        assert config.sound_enabled == False
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = TimerConfig(work_duration=30)
        data = config.to_dict()
        assert data['work_duration'] == 30
        assert 'short_break' in data
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {'work_duration': 30, 'short_break': 10}
        config = TimerConfig.from_dict(data)
        assert config.work_duration == 30
        assert config.short_break == 10


class TestTimerSession:
    """计时会话测试"""
    
    def test_create_session(self):
        """测试创建会话"""
        session = TimerSession(
            id="test-123",
            timer_type=TimerType.COUNTDOWN,
            start_time=datetime.now(),
            duration_seconds=300,
            target_seconds=300,
            completed=True
        )
        assert session.id == "test-123"
        assert session.timer_type == TimerType.COUNTDOWN
        assert session.completed == True
    
    def test_session_to_dict(self):
        """测试会话转字典"""
        session = TimerSession(
            id="test-123",
            timer_type=TimerType.POMODORO,
            start_time=datetime(2025, 1, 1, 12, 0, 0),
            duration_seconds=1500,
            target_seconds=1500,
            completed=True
        )
        data = session.to_dict()
        assert data['id'] == "test-123"
        assert data['timer_type'] == "pomodoro"
        assert data['completed'] == True


class TestCountdownTimer:
    """倒计时器测试"""
    
    def test_create_countdown(self):
        """测试创建倒计时"""
        timer = CountdownTimer(60, title="测试倒计时")
        assert timer.duration == 60
        assert timer.state == TimerState.IDLE
        assert timer.remaining == 60
    
    def test_countdown_progress(self):
        """测试倒计时进度"""
        timer = CountdownTimer(100)
        assert timer.progress == 0.0
        
        # 模拟经过时间
        timer._elapsed = 50
        assert timer.progress == 50.0
    
    def test_countdown_remaining(self):
        """测试剩余时间"""
        timer = CountdownTimer(100)
        timer._elapsed = 30
        assert timer.remaining == 70


class TestStopwatchTimer:
    """秒表测试"""
    
    def test_create_stopwatch(self):
        """测试创建秒表"""
        timer = StopwatchTimer(title="测试秒表")
        assert timer.state == TimerState.IDLE
        assert timer.elapsed == 0
    
    def test_stopwatch_lap(self):
        """测试秒表圈数"""
        timer = StopwatchTimer()
        timer._elapsed = 100
        lap1 = timer.lap()
        assert lap1 == 100
        assert timer.lap_count == 1


class TestPomodoroTimer:
    """番茄钟测试"""
    
    def test_create_pomodoro(self):
        """测试创建番茄钟"""
        config = TimerConfig(work_duration=25, short_break=5, long_break=15)
        timer = PomodoroTimer(config)
        assert timer.work_duration == 25 * 60
        assert timer.short_break_duration == 5 * 60
        assert timer.long_break_duration == 15 * 60
    
    def test_pomodoro_phases(self):
        """测试番茄钟阶段"""
        timer = PomodoroTimer()
        assert timer.current_phase == PomodoroTimer.WORK


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
