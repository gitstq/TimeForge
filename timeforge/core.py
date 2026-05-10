#!/usr/bin/env python3
"""
TimeForge Core - 核心功能模块
"""

import time
import sys
import json
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod


class TimerState(Enum):
    """计时器状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


class TimerType(Enum):
    """计时器类型枚举"""
    COUNTDOWN = "countdown"
    STOPWATCH = "stopwatch"
    POMODORO = "pomodoro"


@dataclass
class TimerConfig:
    """计时器配置数据类"""
    work_duration: int = 25      # 番茄钟工作时间(分钟)
    short_break: int = 5         # 短休息时间(分钟)
    long_break: int = 15         # 长休息时间(分钟)
    sessions_before_long: int = 4 # 长休息前的会话数
    sound_enabled: bool = True
    auto_start_break: bool = False
    auto_start_work: bool = False
    notification_enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TimerConfig':
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class TimerSession:
    """计时会话记录"""
    id: str
    timer_type: TimerType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int = 0
    target_seconds: int = 0
    completed: bool = False
    title: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timer_type': self.timer_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'target_seconds': self.target_seconds,
            'completed': self.completed,
            'title': self.title,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TimerSession':
        return cls(
            id=data['id'],
            timer_type=TimerType(data['timer_type']),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            duration_seconds=data['duration_seconds'],
            target_seconds=data['target_seconds'],
            completed=data['completed'],
            title=data.get('title', ''),
        )


class BaseTimer(ABC):
    """计时器基类"""
    
    def __init__(self, config: Optional[TimerConfig] = None):
        self.config = config or TimerConfig()
        self.state = TimerState.IDLE
        self._start_time: Optional[float] = None
        self._pause_time: float = 0
        self._elapsed: int = 0
        self._stop_event = threading.Event()
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_pause': [],
            'on_resume': [],
            'on_tick': [],
            'on_finish': [],
        }
    
    def on(self, event: str, callback: Callable):
        """注册事件回调"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs):
        """触发事件回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass
    
    @property
    def elapsed(self) -> int:
        """已运行时间(秒)"""
        if self._start_time is None:
            return self._elapsed
        return self._elapsed + int(time.time() - self._start_time - self._pause_time)
    
    @abstractmethod
    def start(self):
        """启动计时器"""
        pass
    
    def pause(self):
        """暂停计时器"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self._elapsed = self.elapsed
            self._start_time = None
            self._emit('on_pause')
    
    def resume(self):
        """恢复计时器"""
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._start_time = time.time()
            self._emit('on_resume')
    
    def stop(self):
        """停止计时器"""
        self._stop_event.set()
        self.state = TimerState.FINISHED
        self._emit('on_finish')
    
    def reset(self):
        """重置计时器"""
        self._start_time = None
        self._pause_time = 0
        self._elapsed = 0
        self.state = TimerState.IDLE
        self._stop_event.clear()


class TimeFormatter:
    """时间格式化工具类"""
    
    @staticmethod
    def format_seconds(seconds: int, show_hours: bool = True) -> str:
        """格式化秒数为可读字符串"""
        seconds = max(0, int(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if show_hours and hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def parse_time_input(time_str: str) -> int:
        """解析时间输入，返回秒数
        
        支持格式:
        - 纯数字: 90 (秒)
        - 带单位: 10s, 5m, 1h, 1h30m
        - 冒号分隔: 5:00, 1:30:00
        """
        import re
        time_str = time_str.strip().lower()
        total_seconds = 0
        
        # 尝试解析 HH:MM:SS 或 MM:SS 格式
        if ':' in time_str:
            parts = time_str.split(':')
            try:
                if len(parts) == 2:
                    minutes, seconds = parts
                    total_seconds = int(minutes) * 60 + int(float(seconds))
                elif len(parts) == 3:
                    hours, minutes, seconds = parts
                    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
                return total_seconds
            except ValueError:
                pass
        
        # 解析带单位的格式
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*h', 3600),
            (r'(\d+(?:\.\d+)?)\s*m', 60),
            (r'(\d+(?:\.\d+)?)\s*s', 1),
        ]
        
        matched = False
        for pattern, multiplier in patterns:
            match = re.search(pattern, time_str)
            if match:
                total_seconds += int(float(match.group(1)) * multiplier)
                matched = True
        
        # 如果没有匹配任何单位
        if not matched:
            try:
                total_seconds = int(float(time_str))
            except ValueError:
                # 默认为分钟
                total_seconds = int(float(time_str) * 60)
        
        return total_seconds


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_NAME = "timeforge_config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".config" / "timeforge" / self.DEFAULT_CONFIG_NAME
        
        self.config = self._load()
    
    def _load(self) -> TimerConfig:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return TimerConfig.from_dict(data)
            except Exception:
                pass
        return TimerConfig()
    
    def save(self):
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config.to_dict(), f, indent=2)
    
    def update(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save()


class SessionManager:
    """会话记录管理器"""
    
    DEFAULT_SESSIONS_FILE = "timeforge_sessions.json"
    
    def __init__(self, data_path: Optional[str] = None):
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = Path.home() / ".local" / "share" / "timeforge" / self.DEFAULT_SESSIONS_FILE
        
        self.sessions: List[TimerSession] = self._load()
    
    def _load(self) -> List[TimerSession]:
        """加载会话记录"""
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [TimerSession.from_dict(s) for s in data]
            except Exception:
                pass
        return []
    
    def save(self):
        """保存会话记录"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump([s.to_dict() for s in self.sessions], f, indent=2)
    
    def add(self, session: TimerSession):
        """添加会话记录"""
        self.sessions.append(session)
        self.save()
    
    def get_stats(self, timer_type: Optional[TimerType] = None) -> Dict:
        """获取统计数据"""
        sessions = self.sessions
        if timer_type:
            sessions = [s for s in sessions if s.timer_type == timer_type]
        
        total_duration = sum(s.duration_seconds for s in sessions)
        completed_count = sum(1 for s in sessions if s.completed)
        
        return {
            'total_sessions': len(sessions),
            'completed_sessions': completed_count,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': TimeFormatter.format_seconds(total_duration),
        }
    
    def clear(self):
        """清空会话记录"""
        self.sessions.clear()
        self.save()
