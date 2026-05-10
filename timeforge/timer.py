#!/usr/bin/env python3
"""
TimeForge Timer - 计时器实现模块
"""

import time
import threading
from typing import Optional, Callable
from datetime import datetime
import uuid

from .core import (
    BaseTimer, TimerConfig, TimerState, TimerType,
    TimerSession, TimeFormatter
)


class CountdownTimer(BaseTimer):
    """倒计时器"""
    
    def __init__(self, duration_seconds: int, config: Optional[TimerConfig] = None, title: str = ""):
        super().__init__(config)
        self.duration = duration_seconds
        self.title = title
        self.session_id = str(uuid.uuid4())[:8]
    
    @property
    def remaining(self) -> int:
        """剩余时间(秒)"""
        return max(0, self.duration - self.elapsed)
    
    @property
    def progress(self) -> float:
        """进度百分比 (0-100)"""
        if self.duration <= 0:
            return 100.0
        return min(100.0, (self.elapsed / self.duration) * 100)
    
    def start(self):
        """启动倒计时"""
        if self.state != TimerState.IDLE:
            return
        
        self.state = TimerState.RUNNING
        self._start_time = time.time()
        self._stop_event.clear()
        self._emit('on_start', self)
        
        # 启动计时线程
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
    
    def _run(self):
        """计时主循环"""
        while not self._stop_event.is_set() and self.state == TimerState.RUNNING:
            if self.remaining <= 0:
                self.state = TimerState.FINISHED
                self._emit('on_finish', self)
                break
            
            self._emit('on_tick', self.elapsed, self.remaining, self.progress)
            time.sleep(0.1)
    
    def get_session(self) -> TimerSession:
        """获取会话记录"""
        return TimerSession(
            id=self.session_id,
            timer_type=TimerType.COUNTDOWN,
            start_time=datetime.fromtimestamp(self._start_time) if self._start_time else datetime.now(),
            end_time=datetime.now() if self.state == TimerState.FINISHED else None,
            duration_seconds=self.elapsed,
            target_seconds=self.duration,
            completed=self.state == TimerState.FINISHED,
            title=self.title,
        )


class StopwatchTimer(BaseTimer):
    """秒表计时器"""
    
    def __init__(self, config: Optional[TimerConfig] = None, title: str = ""):
        super().__init__(config)
        self.title = title
        self.session_id = str(uuid.uuid4())[:8]
        self._laps: list = []
    
    def start(self):
        """启动秒表"""
        if self.state != TimerState.IDLE:
            return
        
        self.state = TimerState.RUNNING
        self._start_time = time.time()
        self._stop_event.clear()
        self._emit('on_start', self)
        
        # 启动计时线程
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
    
    def _run(self):
        """计时主循环"""
        while not self._stop_event.is_set() and self.state == TimerState.RUNNING:
            self._emit('on_tick', self.elapsed)
            time.sleep(0.1)
    
    def lap(self) -> int:
        """记录圈数，返回当前用时"""
        lap_time = self.elapsed
        self._laps.append(lap_time)
        return lap_time
    
    @property
    def laps(self) -> list:
        """获取所有圈数记录"""
        return self._laps.copy()
    
    @property
    def lap_count(self) -> int:
        """获取圈数"""
        return len(self._laps)
    
    def get_session(self) -> TimerSession:
        """获取会话记录"""
        return TimerSession(
            id=self.session_id,
            timer_type=TimerType.STOPWATCH,
            start_time=datetime.fromtimestamp(self._start_time) if self._start_time else datetime.now(),
            end_time=datetime.now() if self.state == TimerState.FINISHED else None,
            duration_seconds=self.elapsed,
            target_seconds=0,
            completed=True,
            title=self.title,
        )


class PomodoroTimer(BaseTimer):
    """番茄钟计时器"""
    
    # 状态枚举
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    
    def __init__(self, config: Optional[TimerConfig] = None):
        super().__init__(config)
        self.current_phase = self.WORK
        self.session_count = 0
        self.total_pomodoros = 0
        self.session_id = str(uuid.uuid4())[:8]
        self._current_timer: Optional[CountdownTimer] = None
    
    @property
    def work_duration(self) -> int:
        """工作时间(秒)"""
        return self.config.work_duration * 60
    
    @property
    def short_break_duration(self) -> int:
        """短休息时间(秒)"""
        return self.config.short_break * 60
    
    @property
    def long_break_duration(self) -> int:
        """长休息时间(秒)"""
        return self.config.long_break * 60
    
    def start(self):
        """启动番茄钟"""
        if self.state != TimerState.IDLE:
            return
        
        self.state = TimerState.RUNNING
        self._start_time = time.time()
        self._emit('on_start', self)
        
        # 开始第一个工作阶段
        self._start_work()
    
    def _start_work(self):
        """开始工作阶段"""
        self.current_phase = self.WORK
        self.session_count += 1
        
        self._current_timer = CountdownTimer(
            self.work_duration,
            self.config,
            title=f"🍅 工作 #{self.session_count}"
        )
        
        # 继承回调
        for event, callbacks in self._callbacks.items():
            for cb in callbacks:
                self._current_timer.on(event, cb)
        
        self._current_timer.on('on_finish', self._on_work_finish)
        self._current_timer.start()
    
    def _on_work_finish(self, timer):
        """工作阶段结束回调"""
        self.total_pomodoros += 1
        
        # 判断休息类型
        if self.session_count % self.config.sessions_before_long == 0:
            self._start_break(is_long=True)
        else:
            self._start_break(is_long=False)
    
    def _start_break(self, is_long: bool = False):
        """开始休息阶段"""
        if is_long:
            self.current_phase = self.LONG_BREAK
            duration = self.long_break_duration
            title = f"☕ 长休息 (完成{self.session_count}个番茄)"
        else:
            self.current_phase = self.SHORT_BREAK
            duration = self.short_break_duration
            title = "☕ 短休息"
        
        self._current_timer = CountdownTimer(
            duration,
            self.config,
            title=title
        )
        
        # 继承回调
        for event, callbacks in self._callbacks.items():
            for cb in callbacks:
                self._current_timer.on(event, cb)
        
        self._current_timer.on('on_finish', self._on_break_finish)
        self._current_timer.start()
    
    def _on_break_finish(self, timer):
        """休息阶段结束回调"""
        if self.config.auto_start_work:
            self._start_work()
        else:
            self.state = TimerState.IDLE
            self._emit('on_phase_complete', self.current_phase)
    
    def skip_break(self):
        """跳过休息"""
        if self.current_phase in (self.SHORT_BREAK, self.LONG_BREAK):
            if self._current_timer:
                self._current_timer.stop()
            self._start_work()
    
    def stop(self):
        """停止番茄钟"""
        if self._current_timer:
            self._current_timer.stop()
        super().stop()
    
    @property
    def elapsed(self) -> int:
        """已运行时间"""
        if self._current_timer:
            return self._current_timer.elapsed
        return 0
    
    @property
    def remaining(self) -> int:
        """剩余时间"""
        if self._current_timer:
            return self._current_timer.remaining
        return 0
    
    @property
    def progress(self) -> float:
        """当前阶段进度"""
        if self._current_timer:
            return self._current_timer.progress
        return 0.0
