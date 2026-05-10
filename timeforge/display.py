#!/usr/bin/env python3
"""
TimeForge Display - 显示模块
"""

import sys
from typing import Optional
from datetime import datetime

# 尝试导入Rich库
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.align import Align
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .core import TimerType, TimerState, TimeFormatter


class TimerDisplay:
    """计时器显示管理器"""
    
    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None
    
    def clear_screen(self):
        """清屏"""
        if self.use_rich:
            self.console.clear()
        else:
            print("\033[2J\033[H", end="")
    
    def render_timer(
        self,
        elapsed: int,
        remaining: int = 0,
        duration: int = 0,
        timer_type: TimerType = TimerType.COUNTDOWN,
        title: str = "",
        state: TimerState = TimerState.RUNNING,
        progress: float = 0.0
    ):
        """渲染计时器显示"""
        if self.use_rich:
            return self._render_rich(elapsed, remaining, duration, timer_type, title, state, progress)
        else:
            return self._render_simple(elapsed, remaining, duration, timer_type, title, state, progress)
    
    def _render_rich(
        self,
        elapsed: int,
        remaining: int,
        duration: int,
        timer_type: TimerType,
        title: str,
        state: TimerState,
        progress: float
    ):
        """Rich渲染"""
        # 选择表情符号
        if timer_type == TimerType.POMODORO:
            if "工作" in title or "work" in title.lower():
                emoji = "🍅"
            else:
                emoji = "☕"
        elif timer_type == TimerType.STOPWATCH:
            emoji = "⏱️"
        else:
            emoji = "⏳"
        
        # 时间显示
        if timer_type == TimerType.STOPWATCH:
            time_str = TimeFormatter.format_seconds(elapsed)
            time_display = Text()
            time_display.append(f"{emoji} ", style="bold")
            time_display.append(time_str, style="bold cyan")
        else:
            time_str = TimeFormatter.format_seconds(remaining)
            time_display = Text()
            time_display.append(f"{emoji} ", style="bold")
            time_display.append(time_str, style="bold cyan")
        
        # 状态标签
        if state == TimerState.PAUSED:
            time_display.append(" [暂停]", style="bold yellow")
        elif state == TimerState.FINISHED:
            time_display.append(" [完成]", style="bold green")
        
        # 进度条
        if timer_type != TimerType.STOPWATCH and duration > 0:
            bar_width = 30
            filled = int(bar_width * progress / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            progress_text = Text()
            progress_text.append(f"[{bar}] ", style="dim")
            progress_text.append(f"{progress:.1f}%", style="bold green")
        else:
            progress_text = Text("秒表模式", style="dim")
        
        # 创建面板
        panel = Panel(
            Align.center(
                Text.assemble(
                    time_display,
                    Text("\n\n"),
                    progress_text,
                    Text(f"\n\n{title}", style="dim italic") if title else Text()
                )
            ),
            title="[bold blue]⏰ TimeForge[/bold blue]",
            border_style="blue",
            padding=(2, 4)
        )
        
        return panel
    
    def _render_simple(
        self,
        elapsed: int,
        remaining: int,
        duration: int,
        timer_type: TimerType,
        title: str,
        state: TimerState,
        progress: float
    ) -> str:
        """简单文本渲染"""
        if timer_type == TimerType.STOPWATCH:
            time_str = TimeFormatter.format_seconds(elapsed)
            emoji = "⏱️"
        else:
            time_str = TimeFormatter.format_seconds(remaining)
            emoji = "⏳"
        
        status = ""
        if state == TimerState.PAUSED:
            status = " [暂停]"
        elif state == TimerState.FINISHED:
            status = " [完成]"
        
        # 进度条
        if timer_type != TimerType.STOPWATCH and duration > 0:
            bar_width = 20
            filled = int(bar_width * progress / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            progress_str = f"[{bar}] {progress:.0f}%"
        else:
            progress_str = ""
        
        lines = [
            "=" * 40,
            f"  {emoji} TimeForge",
            "=" * 40,
            "",
            f"    {time_str}{status}",
            "",
            f"    {progress_str}",
            "",
        ]
        
        if title:
            lines.append(f"    {title}")
        
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def render_stats(self, stats: dict):
        """渲染统计信息"""
        if self.use_rich:
            return self._render_stats_rich(stats)
        else:
            return self._render_stats_simple(stats)
    
    def _render_stats_rich(self, stats: dict):
        """Rich统计渲染"""
        table = Table(title="📊 时间统计")
        table.add_column("指标", style="cyan")
        table.add_column("数值", justify="right", style="green")
        
        table.add_row("总会话数", str(stats.get('total_sessions', 0)))
        table.add_row("完成会话数", str(stats.get('completed_sessions', 0)))
        table.add_row("总时长", stats.get('total_duration_formatted', '00:00'))
        
        return table
    
    def _render_stats_simple(self, stats: dict):
        """简单统计渲染"""
        lines = [
            "",
            "📊 时间统计",
            "=" * 40,
            f"  总会话数: {stats.get('total_sessions', 0)}",
            f"  完成会话数: {stats.get('completed_sessions', 0)}",
            f"  总时长: {stats.get('total_duration_formatted', '00:00')}",
            "=" * 40,
        ]
        return "\n".join(lines)
    
    def print(self, content):
        """打印内容"""
        if self.use_rich:
            self.console.print(content)
        else:
            print(content)
    
    def print_error(self, message: str):
        """打印错误信息"""
        if self.use_rich:
            self.console.print(f"[bold red]错误: {message}[/bold red]")
        else:
            print(f"错误: {message}")
    
    def print_success(self, message: str):
        """打印成功信息"""
        if self.use_rich:
            self.console.print(f"[bold green]{message}[/bold green]")
        else:
            print(message)
    
    def print_warning(self, message: str):
        """打印警告信息"""
        if self.use_rich:
            self.console.print(f"[bold yellow]{message}[/bold yellow]")
        else:
            print(f"警告: {message}")
    
    def print_info(self, message: str):
        """打印信息"""
        if self.use_rich:
            self.console.print(f"[blue]{message}[/blue]")
        else:
            print(message)
