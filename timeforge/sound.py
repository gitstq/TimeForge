#!/usr/bin/env python3
"""
TimeForge Sound - 声音管理模块
"""

import sys
import threading
import time
from typing import Optional
from pathlib import Path

# 平台检测
import platform
SYSTEM = platform.system()

# Windows声音支持
if SYSTEM == "Windows":
    try:
        import winsound
        WINDOWS_SOUND = True
    except ImportError:
        WINDOWS_SOUND = False
else:
    WINDOWS_SOUND = False

# macOS/Linux声音支持
if SYSTEM != "Windows":
    try:
        import subprocess
        # 检查是否有可用的声音播放工具
        LINUX_SOUND = True
    except ImportError:
        LINUX_SOUND = False


class SoundManager:
    """声音管理器"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._playing = False
    
    def play_beep(self, frequency: int = 1000, duration: int = 200, times: int = 1):
        """播放蜂鸣声
        
        Args:
            frequency: 频率(Hz)，仅Windows有效
            duration: 持续时间(毫秒)
            times: 重复次数
        """
        if not self.enabled:
            return
        
        def _play():
            self._playing = True
            for _ in range(times):
                self._beep(frequency, duration)
                time.sleep(0.1)
            self._playing = False
        
        # 在后台线程播放
        thread = threading.Thread(target=_play, daemon=True)
        thread.start()
    
    def _beep(self, frequency: int, duration: int):
        """实际播放蜂鸣声"""
        if SYSTEM == "Windows" and WINDOWS_SOUND:
            try:
                winsound.Beep(frequency, duration)
                return
            except Exception:
                pass
        
        # 尝试系统蜂鸣
        try:
            sys.stdout.write('\a')
            sys.stdout.flush()
        except Exception:
            pass
        
        # Linux/macOS尝试使用系统工具
        if SYSTEM == "Darwin":  # macOS
            try:
                subprocess.run(
                    ['afplay', '/System/Library/Sounds/Ping.aiff'],
                    capture_output=True,
                    timeout=2
                )
            except Exception:
                pass
        elif SYSTEM == "Linux":
            try:
                # 尝试使用paplay (PulseAudio)
                subprocess.run(
                    ['paplay', '/usr/share/sounds/freedesktop/stereo/complete.oga'],
                    capture_output=True,
                    timeout=2
                )
            except Exception:
                pass
            try:
                # 尝试使用aplay (ALSA)
                subprocess.run(
                    ['aplay', '-q', '/usr/share/sounds/alsa/Front_Center.wav'],
                    capture_output=True,
                    timeout=2
                )
            except Exception:
                pass
    
    def play_start(self):
        """播放开始声音"""
        self.play_beep(800, 100, 1)
    
    def play_pause(self):
        """播放暂停声音"""
        self.play_beep(600, 150, 2)
    
    def play_finish(self):
        """播放完成声音"""
        self.play_beep(1000, 200, 3)
    
    def play_tick(self):
        """播放滴答声"""
        self.play_beep(500, 50, 1)
    
    def play_lap(self):
        """播放圈数记录声音"""
        self.play_beep(900, 100, 1)
    
    def enable(self):
        """启用声音"""
        self.enabled = True
    
    def disable(self):
        """禁用声音"""
        self.enabled = False
    
    @property
    def is_playing(self) -> bool:
        """是否正在播放"""
        return self._playing
