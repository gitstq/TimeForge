#!/usr/bin/env python3
"""
TimeForge Stats - 统计模块
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import defaultdict

from .core import TimerSession, TimerType, TimeFormatter


class StatsManager:
    """统计管理器"""
    
    def __init__(self, sessions: List[TimerSession]):
        self.sessions = sessions
    
    def get_overall_stats(self) -> Dict:
        """获取总体统计"""
        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for s in self.sessions if s.completed)
        total_duration = sum(s.duration_seconds for s in self.sessions)
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': TimeFormatter.format_seconds(total_duration),
        }
    
    def get_stats_by_type(self) -> Dict[TimerType, Dict]:
        """按类型获取统计"""
        stats = defaultdict(lambda: {
            'count': 0,
            'completed': 0,
            'total_duration': 0,
        })
        
        for session in self.sessions:
            stats[session.timer_type]['count'] += 1
            if session.completed:
                stats[session.timer_type]['completed'] += 1
            stats[session.timer_type]['total_duration'] += session.duration_seconds
        
        # 格式化输出
        result = {}
        for timer_type, data in stats.items():
            result[timer_type] = {
                'count': data['count'],
                'completed': data['completed'],
                'total_duration_seconds': data['total_duration'],
                'total_duration_formatted': TimeFormatter.format_seconds(data['total_duration']),
            }
        
        return result
    
    def get_daily_stats(self, days: int = 7) -> Dict:
        """获取每日统计"""
        today = datetime.now().date()
        daily_stats = {}
        
        for i in range(days):
            date = today - timedelta(days=i)
            daily_stats[date.isoformat()] = {
                'date': date.isoformat(),
                'sessions': 0,
                'duration_seconds': 0,
            }
        
        for session in self.sessions:
            if session.start_time:
                date = session.start_time.date()
                date_str = date.isoformat()
                if date_str in daily_stats:
                    daily_stats[date_str]['sessions'] += 1
                    daily_stats[date_str]['duration_seconds'] += session.duration_seconds
        
        # 格式化
        for date_str in daily_stats:
            daily_stats[date_str]['duration_formatted'] = TimeFormatter.format_seconds(
                daily_stats[date_str]['duration_seconds']
            )
        
        return daily_stats
    
    def get_pomodoro_stats(self) -> Dict:
        """获取番茄钟专项统计"""
        pomodoro_sessions = [s for s in self.sessions if s.timer_type == TimerType.POMODORO]
        
        total_pomodoros = sum(1 for s in pomodoro_sessions if s.completed)
        total_work_time = sum(s.duration_seconds for s in pomodoro_sessions)
        
        # 计算平均每日番茄数
        if pomodoro_sessions:
            dates = set(s.start_time.date() for s in pomodoro_sessions if s.start_time)
            avg_daily = total_pomodoros / len(dates) if dates else 0
        else:
            avg_daily = 0
        
        return {
            'total_pomodoros': total_pomodoros,
            'total_work_time_seconds': total_work_time,
            'total_work_time_formatted': TimeFormatter.format_seconds(total_work_time),
            'average_daily_pomodoros': round(avg_daily, 1),
        }
    
    def get_streak(self) -> Dict:
        """获取连续使用天数"""
        if not self.sessions:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # 获取所有使用日期
        dates = sorted(set(s.start_time.date() for s in self.sessions if s.start_time))
        
        if not dates:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # 计算当前连续天数
        today = datetime.now().date()
        current_streak = 0
        
        for i, date in enumerate(reversed(dates)):
            expected_date = today - timedelta(days=i)
            if date == expected_date:
                current_streak += 1
            else:
                break
        
        # 计算最长连续天数
        longest_streak = 1
        current = 1
        
        for i in range(1, len(dates)):
            if dates[i] - dates[i-1] == timedelta(days=1):
                current += 1
                longest_streak = max(longest_streak, current)
            else:
                current = 1
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
        }
    
    def get_summary(self) -> str:
        """获取统计摘要文本"""
        overall = self.get_overall_stats()
        by_type = self.get_stats_by_type()
        streak = self.get_streak()
        
        lines = [
            "📊 TimeForge 统计摘要",
            "=" * 40,
            "",
            f"  总会话数: {overall['total_sessions']}",
            f"  完成会话: {overall['completed_sessions']}",
            f"  总时长: {overall['total_duration_formatted']}",
            "",
            "📈 按类型统计:",
        ]
        
        for timer_type, stats in by_type.items():
            lines.append(f"  {timer_type.value}: {stats['count']}次, {stats['total_duration_formatted']}")
        
        lines.extend([
            "",
            f"🔥 当前连续: {streak['current_streak']}天",
            f"🏆 最长连续: {streak['longest_streak']}天",
            "",
            "=" * 40,
        ])
        
        return "\n".join(lines)
