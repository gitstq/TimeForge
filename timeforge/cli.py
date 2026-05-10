#!/usr/bin/env python3
"""
TimeForge CLI - 命令行入口
"""

import argparse
import sys
import signal
from typing import Optional

from .core import (
    TimeFormatter, TimerConfig, TimerType, TimerSession,
    ConfigManager, SessionManager
)
from .timer import CountdownTimer, StopwatchTimer, PomodoroTimer
from .display import TimerDisplay
from .sound import SoundManager
from .stats import StatsManager

# Rich库检测
try:
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TimeForgeCLI:
    """TimeForge命令行接口"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.session_manager = SessionManager()
        self.display = TimerDisplay(use_rich=True)
        self.sound = SoundManager(self.config_manager.config.sound_enabled)
        self.running = False
    
    def countdown(self, duration_str: str, title: str = "倒计时"):
        """运行倒计时"""
        try:
            duration = TimeFormatter.parse_time_input(duration_str)
        except ValueError as e:
            self.display.print_error(f"无效的时间格式: {duration_str}")
            return
        
        if duration <= 0:
            self.display.print_error("时长必须大于0")
            return
        
        timer = CountdownTimer(duration, self.config_manager.config, title)
        self._run_timer(timer, TimerType.COUNTDOWN)
    
    def stopwatch(self, title: str = "秒表"):
        """运行秒表"""
        timer = StopwatchTimer(self.config_manager.config, title)
        self._run_timer(timer, TimerType.STOPWATCH)
    
    def pomodoro(self, work_duration: Optional[int] = None):
        """运行番茄钟"""
        config = self.config_manager.config
        if work_duration:
            config.work_duration = work_duration
        
        timer = PomodoroTimer(config)
        self._run_timer(timer, TimerType.POMODORO)
    
    def _run_timer(self, timer, timer_type: TimerType):
        """运行计时器"""
        self.running = True
        
        # 设置信号处理
        def signal_handler(sig, frame):
            self.running = False
            timer.stop()
            print("\n")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # 设置回调
        timer.on('on_finish', lambda t: self._on_timer_finish(t))
        
        # 显示初始界面
        self.display.clear_screen()
        
        if RICH_AVAILABLE and self.display.use_rich:
            self._run_with_rich(timer, timer_type)
        else:
            self._run_simple(timer, timer_type)
    
    def _run_with_rich(self, timer, timer_type: TimerType):
        """使用Rich运行计时器"""
        from rich.live import Live
        
        def generate_display():
            if timer_type == TimerType.STOPWATCH:
                return self.display.render_timer(
                    elapsed=timer.elapsed,
                    timer_type=timer_type,
                    title=getattr(timer, 'title', '秒表'),
                    state=timer.state
                )
            else:
                return self.display.render_timer(
                    elapsed=timer.elapsed,
                    remaining=getattr(timer, 'remaining', 0),
                    duration=getattr(timer, 'duration', 0),
                    timer_type=timer_type,
                    title=getattr(timer, 'title', ''),
                    state=timer.state,
                    progress=getattr(timer, 'progress', 0)
                )
        
        timer.start()
        
        try:
            with Live(generate_display(), console=self.display.console, refresh_per_second=4) as live:
                while timer.state.value in ('running', 'paused'):
                    live.update(generate_display())
                    import time
                    time.sleep(0.25)
        except Exception:
            pass
        
        # 保存会话
        if hasattr(timer, 'get_session'):
            self.session_manager.add(timer.get_session())
        
        # 播放完成声音
        self.sound.play_finish()
        
        # 显示完成信息
        self.display.print_success("\n⏰ 计时完成!")
    
    def _run_simple(self, timer, timer_type: TimerType):
        """简单模式运行计时器"""
        import time
        
        timer.start()
        
        try:
            while timer.state.value in ('running', 'paused'):
                if timer_type == TimerType.STOPWATCH:
                    print(f"\r⏱️  {TimeFormatter.format_seconds(timer.elapsed)}", end="", flush=True)
                else:
                    remaining = getattr(timer, 'remaining', 0)
                    print(f"\r⏳ 剩余: {TimeFormatter.format_seconds(remaining)}", end="", flush=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            timer.stop()
        
        print("\n")
        
        # 保存会话
        if hasattr(timer, 'get_session'):
            self.session_manager.add(timer.get_session())
        
        # 播放完成声音
        self.sound.play_finish()
        
        print("⏰ 计时完成!")
    
    def _on_timer_finish(self, timer):
        """计时器完成回调"""
        self.running = False
        self.sound.play_finish()
    
    def show_stats(self):
        """显示统计信息"""
        stats_manager = StatsManager(self.session_manager.sessions)
        
        if not self.session_manager.sessions:
            self.display.print_warning("暂无统计数据，开始使用TimeForge来记录你的时间吧！")
            return
        
        self.display.print(stats_manager.get_summary())
    
    def config_cmd(self, **kwargs):
        """配置命令"""
        if not kwargs:
            # 显示当前配置
            config = self.config_manager.config
            print("\n⚙️ 当前配置:")
            print(f"  工作时长: {config.work_duration} 分钟")
            print(f"  短休息: {config.short_break} 分钟")
            print(f"  长休息: {config.long_break} 分钟")
            print(f"  长休息前会话数: {config.sessions_before_long}")
            print(f"  声音: {'开启' if config.sound_enabled else '关闭'}")
            print(f"  自动开始休息: {'是' if config.auto_start_break else '否'}")
            print(f"  自动开始工作: {'是' if config.auto_start_work else '否'}")
            return
        
        # 更新配置
        self.config_manager.update(**kwargs)
        self.display.print_success("配置已更新!")
    
    def clear_stats(self):
        """清空统计数据"""
        self.session_manager.clear()
        self.display.print_success("统计数据已清空!")


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="timeforge",
        description="⏰ TimeForge - 终端时间管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  timeforge countdown 10m           # 10分钟倒计时
  timeforge countdown 1h30m         # 1小时30分钟倒计时
  timeforge countdown 90            # 90秒倒计时
  timeforge countdown 5:00          # 5分钟倒计时
  timeforge stopwatch               # 启动秒表
  timeforge pomodoro                # 启动番茄钟
  timeforge pomodoro -w 30          # 30分钟工作时间的番茄钟
  timeforge stats                   # 显示统计
  timeforge config                  # 显示当前配置
  timeforge config -w 30 -s 10      # 设置工作30分钟，短休息10分钟
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="禁用声音提示"
    )
    
    parser.add_argument(
        "--no-rich",
        action="store_true",
        help="禁用Rich显示(使用简单文本模式)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 倒计时命令
    countdown_parser = subparsers.add_parser(
        "countdown", 
        help="启动倒计时",
        description="启动一个倒计时器"
    )
    countdown_parser.add_argument(
        "duration",
        help="倒计时时长 (如: 10m, 1h, 90s, 5:00, 1:30:00)"
    )
    countdown_parser.add_argument(
        "-t", "--title",
        default="倒计时",
        help="计时器标题"
    )
    
    # 秒表命令
    stopwatch_parser = subparsers.add_parser(
        "stopwatch",
        help="启动秒表",
        description="启动一个秒表计时器"
    )
    stopwatch_parser.add_argument(
        "-t", "--title",
        default="秒表",
        help="计时器标题"
    )
    
    # 番茄钟命令
    pomodoro_parser = subparsers.add_parser(
        "pomodoro",
        help="启动番茄钟",
        description="启动番茄钟计时器"
    )
    pomodoro_parser.add_argument(
        "-w", "--work",
        type=int,
        metavar="MINUTES",
        help="工作时间(分钟)"
    )
    pomodoro_parser.add_argument(
        "-s", "--short-break",
        type=int,
        metavar="MINUTES",
        help="短休息时间(分钟)"
    )
    pomodoro_parser.add_argument(
        "-l", "--long-break",
        type=int,
        metavar="MINUTES",
        help="长休息时间(分钟)"
    )
    
    # 统计命令
    stats_parser = subparsers.add_parser(
        "stats",
        help="显示时间统计",
        description="显示使用统计信息"
    )
    stats_parser.add_argument(
        "--clear",
        action="store_true",
        help="清空统计数据"
    )
    
    # 配置命令
    config_parser = subparsers.add_parser(
        "config",
        help="配置TimeForge",
        description="查看或修改配置"
    )
    config_parser.add_argument(
        "-w", "--work",
        type=int,
        metavar="MINUTES",
        help="设置工作时间(分钟)"
    )
    config_parser.add_argument(
        "-s", "--short-break",
        type=int,
        metavar="MINUTES",
        help="设置短休息时间(分钟)"
    )
    config_parser.add_argument(
        "-l", "--long-break",
        type=int,
        metavar="MINUTES",
        help="设置长休息时间(分钟)"
    )
    config_parser.add_argument(
        "--sound",
        type=lambda x: x.lower() in ('true', 'yes', '1', 'on'),
        metavar="ON/OFF",
        help="启用/禁用声音 (true/false)"
    )
    config_parser.add_argument(
        "--auto-break",
        type=lambda x: x.lower() in ('true', 'yes', '1', 'on'),
        metavar="ON/OFF",
        help="自动开始休息"
    )
    
    return parser


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = TimeForgeCLI()
    
    # 处理全局选项
    if args.no_sound:
        cli.sound.disable()
    if args.no_rich:
        cli.display.use_rich = False
    
    # 执行命令
    if args.command == "countdown":
        cli.countdown(args.duration, args.title)
    
    elif args.command == "stopwatch":
        cli.stopwatch(args.title)
    
    elif args.command == "pomodoro":
        config_kwargs = {}
        if args.work:
            config_kwargs['work_duration'] = args.work
        if args.short_break:
            config_kwargs['short_break'] = args.short_break
        if args.long_break:
            config_kwargs['long_break'] = args.long_break
        
        if config_kwargs:
            cli.config_manager.update(**config_kwargs)
        
        cli.pomodoro(args.work)
    
    elif args.command == "stats":
        if hasattr(args, 'clear') and args.clear:
            cli.clear_stats()
        else:
            cli.show_stats()
    
    elif args.command == "config":
        config_kwargs = {}
        if args.work:
            config_kwargs['work_duration'] = args.work
        if args.short_break:
            config_kwargs['short_break'] = args.short_break
        if args.long_break:
            config_kwargs['long_break'] = args.long_break
        if args.sound is not None:
            config_kwargs['sound_enabled'] = args.sound
        if args.auto_break is not None:
            config_kwargs['auto_start_break'] = args.auto_break
        
        cli.config_cmd(**config_kwargs)


if __name__ == "__main__":
    main()
