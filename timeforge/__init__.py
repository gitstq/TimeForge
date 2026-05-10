#!/usr/bin/env python3
"""
TimeForge - 终端时间管理工具
一个功能丰富的终端倒计时、秒表、番茄钟工具
"""

import time
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum
import threading
import signal

# 尝试导入可选依赖
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.live import Live
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import winsound
    WINDOWS = True
except ImportError:
    WINDOWS = False


class TimerState(Enum):
    """计时器状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


class TimerType(Enum):
    """计时器类型"""
    COUNTDOWN = "countdown"
    STOPWATCH = "stopwatch"
    POMODORO = "pomodoro"


@dataclass
class TimerConfig:
    """计时器配置"""
    work_duration: int = 25  # 番茄钟工作时间(分钟)
    short_break: int = 5     # 短休息时间(分钟)
    long_break: int = 15     # 长休息时间(分钟)
    sessions: int = 4        # 长休息前的会话数
    sound_enabled: bool = True
    auto_start_break: bool = False
    auto_start_work: bool = False


@dataclass
class TimerSession:
    """计时会话记录"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int = 0
    timer_type: str = "countdown"
    completed: bool = False


class TimeForge:
    """TimeForge 终端时间管理工具"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.console = Console() if RICH_AVAILABLE else None
        self.config = self._load_config(config_path)
        self.sessions: List[TimerSession] = []
        self.running = False
        self._stop_event = threading.Event()
        
    def _load_config(self, config_path: Optional[str]) -> TimerConfig:
        """加载配置文件"""
        config = TimerConfig()
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
            except Exception:
                pass
        
        return config
    
    def _save_config(self, config_path: str):
        """保存配置文件"""
        try:
            data = {
                'work_duration': self.config.work_duration,
                'short_break': self.config.short_break,
                'long_break': self.config.long_break,
                'sessions': self.config.sessions,
                'sound_enabled': self.config.sound_enabled,
                'auto_start_break': self.config.auto_start_break,
                'auto_start_work': self.config.auto_start_work,
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def _play_sound(self, times: int = 3):
        """播放提示音"""
        if not self.config.sound_enabled:
            return
            
        for _ in range(times):
            if WINDOWS:
                try:
                    winsound.Beep(1000, 200)
                except Exception:
                    pass
            else:
                # Linux/macOS 使用系统蜂鸣
                try:
                    sys.stdout.write('\a')
                    sys.stdout.flush()
                except Exception:
                    pass
            time.sleep(0.1)
    
    def _format_time(self, seconds: int) -> str:
        """格式化时间显示"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def _parse_time_input(self, time_str: str) -> int:
        """解析时间输入，返回秒数"""
        time_str = time_str.strip().lower()
        
        # 支持格式: 10s, 5m, 1h, 1h30m, 90, 1:30, 1:30:00
        total_seconds = 0
        
        # 尝试解析 HH:MM:SS 或 MM:SS 格式
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                total_seconds = int(minutes) * 60 + int(seconds)
            elif len(parts) == 3:
                hours, minutes, seconds = parts
                total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            return total_seconds
        
        # 解析带单位的格式
        import re
        patterns = [
            (r'(\d+)h', 3600),
            (r'(\d+)m', 60),
            (r'(\d+)s', 1),
        ]
        
        matched = False
        for pattern, multiplier in patterns:
            match = re.search(pattern, time_str)
            if match:
                total_seconds += int(match.group(1)) * multiplier
                matched = True
        
        # 如果没有单位，默认为秒
        if not matched:
            try:
                total_seconds = int(time_str)
            except ValueError:
                # 默认为分钟
                total_seconds = int(float(time_str) * 60)
        
        return total_seconds
    
    def countdown(self, duration_str: str, title: str = "倒计时"):
        """倒计时"""
        duration = self._parse_time_input(duration_str)
        self._run_timer(duration, TimerType.COUNTDOWN, title)
    
    def stopwatch(self, title: str = "秒表"):
        """秒表"""
        self._run_timer(0, TimerType.STOPWATCH, title)
    
    def pomodoro(self, custom_work: Optional[int] = None):
        """番茄钟"""
        work_duration = (custom_work or self.config.work_duration) * 60
        session_count = 0
        
        while True:
            # 工作时间
            session_count += 1
            self._run_timer(
                work_duration, 
                TimerType.POMODORO, 
                f"🍅 工作 #{session_count}"
            )
            
            # 记录会话
            self.sessions.append(TimerSession(
                start_time=datetime.now(),
                duration=work_duration,
                timer_type="pomodoro",
                completed=True
            ))
            
            # 判断休息类型
            if session_count % self.config.sessions == 0:
                break_duration = self.config.long_break * 60
                break_title = f"☕ 长休息 (第{session_count}个番茄后)"
            else:
                break_duration = self.config.short_break * 60
                break_title = f"☕ 短休息"
            
            # 休息时间
            self._run_timer(break_duration, TimerType.POMODORO, break_title)
            
            # 询问是否继续
            if not self._ask_continue():
                break
    
    def _ask_continue(self) -> bool:
        """询问是否继续"""
        if self.console:
            self.console.print("\n[bold yellow]是否继续下一个番茄?[/bold yellow] (y/n)")
        else:
            print("\n是否继续下一个番茄? (y/n)")
        
        try:
            response = input().strip().lower()
            return response in ['y', 'yes', '是']
        except:
            return False
    
    def _run_timer(self, duration: int, timer_type: TimerType, title: str):
        """运行计时器"""
        self.running = True
        self._stop_event.clear()
        
        start_time = time.time()
        elapsed = 0
        remaining = duration
        
        if RICH_AVAILABLE and self.console:
            self._run_rich_timer(duration, timer_type, title, start_time)
        else:
            self._run_simple_timer(duration, timer_type, title, start_time)
    
    def _run_rich_timer(self, duration: int, timer_type: TimerType, title: str, start_time: float):
        """使用Rich库运行计时器"""
        elapsed = 0
        remaining = duration
        paused = False
        pause_time = 0
        
        def generate_display():
            if timer_type == TimerType.STOPWATCH:
                time_str = self._format_time(elapsed)
                progress_pct = 100
            else:
                time_str = self._format_time(remaining)
                progress_pct = (elapsed / duration * 100) if duration > 0 else 100
            
            # 创建显示面板
            if timer_type == TimerType.POMODORO:
                emoji = "🍅" if "工作" in title else "☕"
            elif timer_type == TimerType.STOPWATCH:
                emoji = "⏱️"
            else:
                emoji = "⏳"
            
            # 主时间显示
            time_display = Text()
            time_display.append(f"{emoji} ", style="bold")
            time_display.append(time_str, style="bold cyan" if not paused else "bold yellow")
            
            if paused:
                time_display.append(" [暂停]", style="yellow")
            
            # 进度条
            if timer_type != TimerType.STOPWATCH and duration > 0:
                bar_width = 40
                filled = int(bar_width * elapsed / duration)
                bar = "█" * filled + "░" * (bar_width - filled)
                progress_text = Text()
                progress_text.append(f"[{bar}] ", style="dim")
                progress_text.append(f"{progress_pct:.1f}%", style="bold green")
            else:
                progress_text = Text("秒表模式", style="dim")
            
            # 创建面板
            panel = Panel(
                Align.center(
                    Text.assemble(
                        time_display,
                        Text("\n\n"),
                        progress_text,
                        Text(f"\n\n{title}", style="dim italic")
                    )
                ),
                title="[bold blue]TimeForge[/bold blue]",
                border_style="blue",
                padding=(2, 4)
            )
            
            return panel
        
        try:
            with Live(generate_display(), console=self.console, refresh_per_second=4) as live:
                while self.running:
                    if not paused:
                        current_time = time.time()
                        
                        if timer_type == TimerType.STOPWATCH:
                            elapsed = int(current_time - start_time - pause_time)
                        else:
                            elapsed = int(current_time - start_time - pause_time)
                            remaining = max(0, duration - elapsed)
                            
                            if remaining <= 0:
                                self._play_sound(3)
                                self.running = False
                                break
                        
                        live.update(generate_display())
                    
                    time.sleep(0.25)
                    
        except KeyboardInterrupt:
            self.running = False
    
    def _run_simple_timer(self, duration: int, timer_type: TimerType, title: str, start_time: float):
        """简单文本模式计时器"""
        elapsed = 0
        remaining = duration
        
        print(f"\n{title}")
        print("=" * 40)
        print("按 Ctrl+C 停止\n")
        
        try:
            while self.running:
                current_time = time.time()
                
                if timer_type == TimerType.STOPWATCH:
                    elapsed = int(current_time - start_time)
                    print(f"\r⏱️  {self._format_time(elapsed)}", end="", flush=True)
                else:
                    elapsed = int(current_time - start_time)
                    remaining = max(0, duration - elapsed)
                    print(f"\r⏳ 剩余: {self._format_time(remaining)}", end="", flush=True)
                    
                    if remaining <= 0:
                        print("\n\n⏰ 时间到!")
                        self._play_sound(3)
                        break
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n计时器已停止")
        
        self.running = False
    
    def show_stats(self):
        """显示统计信息"""
        if not self.sessions:
            if self.console:
                self.console.print("[yellow]暂无统计数据[/yellow]")
            else:
                print("暂无统计数据")
            return
        
        if RICH_AVAILABLE and self.console:
            table = Table(title="📊 时间统计")
            table.add_column("类型", style="cyan")
            table.add_column("次数", justify="right")
            table.add_column("总时长", justify="right")
            
            stats = {}
            for session in self.sessions:
                t = session.timer_type
                if t not in stats:
                    stats[t] = {'count': 0, 'total': 0}
                stats[t]['count'] += 1
                stats[t]['total'] += session.duration
            
            for t, data in stats.items():
                table.add_row(
                    t,
                    str(data['count']),
                    self._format_time(data['total'])
                )
            
            self.console.print(table)
        else:
            print("\n📊 时间统计")
            print("=" * 40)
            
            stats = {}
            for session in self.sessions:
                t = session.timer_type
                if t not in stats:
                    stats[t] = {'count': 0, 'total': 0}
                stats[t]['count'] += 1
                stats[t]['total'] += session.duration
            
            for t, data in stats.items():
                print(f"{t}: {data['count']}次, 总时长: {self._format_time(data['total'])}")
    
    def stop(self):
        """停止计时器"""
        self.running = False
        self._stop_event.set()


def main():
    parser = argparse.ArgumentParser(
        description="TimeForge - 终端时间管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s countdown 10m          # 10分钟倒计时
  %(prog)s countdown 1h30m        # 1小时30分钟倒计时
  %(prog)s countdown 90           # 90秒倒计时
  %(prog)s countdown 5:00         # 5分钟倒计时
  %(prog)s stopwatch              # 启动秒表
  %(prog)s pomodoro               # 启动番茄钟
  %(prog)s pomodoro -w 30         # 30分钟工作时间的番茄钟
  %(prog)s stats                  # 显示统计
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 倒计时命令
    countdown_parser = subparsers.add_parser("countdown", help="启动倒计时")
    countdown_parser.add_argument("duration", help="倒计时时长 (如: 10m, 1h, 90s, 5:00)")
    countdown_parser.add_argument("-t", "--title", default="倒计时", help="计时器标题")
    
    # 秒表命令
    stopwatch_parser = subparsers.add_parser("stopwatch", help="启动秒表")
    stopwatch_parser.add_argument("-t", "--title", default="秒表", help="计时器标题")
    
    # 番茄钟命令
    pomodoro_parser = subparsers.add_parser("pomodoro", help="启动番茄钟")
    pomodoro_parser.add_argument("-w", "--work", type=int, help="工作时间(分钟)")
    pomodoro_parser.add_argument("-s", "--short-break", type=int, help="短休息时间(分钟)")
    pomodoro_parser.add_argument("-l", "--long-break", type=int, help="长休息时间(分钟)")
    
    # 统计命令
    subparsers.add_parser("stats", help="显示时间统计")
    
    # 配置选项
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("--no-sound", action="store_true", help="禁用提示音")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建实例
    forge = TimeForge(args.config)
    
    if args.no_sound:
        forge.config.sound_enabled = False
    
    # 执行命令
    if args.command == "countdown":
        forge.countdown(args.duration, args.title)
    elif args.command == "stopwatch":
        forge.stopwatch(args.title)
    elif args.command == "pomodoro":
        if args.work:
            forge.config.work_duration = args.work
        if args.short_break:
            forge.config.short_break = args.short_break
        if args.long_break:
            forge.config.long_break = args.long_break
        forge.pomodoro()
    elif args.command == "stats":
        forge.show_stats()


if __name__ == "__main__":
    main()
