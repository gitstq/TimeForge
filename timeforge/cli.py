"""Command-line interface for TimeForge.

Provides the main CLI entry point using argparse with subcommands for
time tracking, pomodoro timer, report generation, analytics, and
git integration.
"""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .core.tracker import TimeTracker
from .core.storage import Storage
from .features.pomodoro import PomodoroTimer
from .features.report import ReportGenerator
from .features.analytics import AnalyticsEngine
from .features.gitlink import GitLinker
from .utils.display import Display, Colors
from .utils.config import Config


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for TimeForge CLI.

    Sets up all subcommands and their arguments:
    - start, stop, pause, resume, status, log, list, delete, edit
    - pomo (start, stop, status, config)
    - report (daily, weekly, monthly)
    - analyze
    - git (link, log)
    - config

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="timeforge",
        description="TimeForge - Lightweight terminal time tracking "
                    "and productivity analysis tool.",
        epilog="Use 'timeforge <command> --help' for more information "
               "on a specific command.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"TimeForge v{__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )

    # ── start command ─────────────────────────────────────────────────
    start_parser = subparsers.add_parser(
        "start",
        help="Start tracking time for a project",
    )
    start_parser.add_argument(
        "project",
        help="Project name to track",
    )
    start_parser.add_argument(
        "description",
        nargs="?",
        default="",
        help="Description of the work (optional)",
    )

    # ── stop command ──────────────────────────────────────────────────
    subparsers.add_parser(
        "stop",
        help="Stop the current tracking session",
    )

    # ── pause command ─────────────────────────────────────────────────
    subparsers.add_parser(
        "pause",
        help="Pause the current tracking session",
    )

    # ── resume command ────────────────────────────────────────────────
    subparsers.add_parser(
        "resume",
        help="Resume a paused tracking session",
    )

    # ── status command ────────────────────────────────────────────────
    subparsers.add_parser(
        "status",
        help="Show current tracking status",
    )

    # ── log command ───────────────────────────────────────────────────
    log_parser = subparsers.add_parser(
        "log",
        help="View time log for a date",
    )
    log_parser.add_argument(
        "date",
        nargs="?",
        default=None,
        help="Date in YYYY-MM-DD format (default: today)",
    )

    # ── list command ──────────────────────────────────────────────────
    subparsers.add_parser(
        "list",
        help="List all projects",
    )

    # ── delete command ────────────────────────────────────────────────
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a time entry",
    )
    delete_parser.add_argument(
        "id",
        help="Entry ID to delete",
    )

    # ── edit command ──────────────────────────────────────────────────
    edit_parser = subparsers.add_parser(
        "edit",
        help="Edit a time entry",
    )
    edit_parser.add_argument(
        "id",
        help="Entry ID to edit",
    )
    edit_parser.add_argument(
        "--project", "-p",
        default=None,
        help="New project name",
    )
    edit_parser.add_argument(
        "--description", "-d",
        default=None,
        help="New description",
    )
    edit_parser.add_argument(
        "--start",
        default=None,
        help="New start time (ISO format)",
    )
    edit_parser.add_argument(
        "--end",
        default=None,
        help="New end time (ISO format)",
    )

    # ── pomo (pomodoro) command ───────────────────────────────────────
    pomo_parser = subparsers.add_parser(
        "pomo",
        help="Pomodoro timer commands",
    )
    pomo_subparsers = pomo_parser.add_subparsers(
        dest="pomo_command",
        help="Pomodoro subcommands",
    )

    pomo_start = pomo_subparsers.add_parser(
        "start",
        help="Start a pomodoro work session",
    )
    pomo_start.add_argument(
        "duration",
        nargs="?",
        type=int,
        default=None,
        help="Work duration in minutes (default: 25)",
    )

    pomo_subparsers.add_parser(
        "stop",
        help="Stop the current pomodoro session",
    )

    pomo_subparsers.add_parser(
        "status",
        help="Show pomodoro timer status",
    )

    pomo_subparsers.add_parser(
        "config",
        help="Show pomodoro configuration",
    )

    # ── report command ────────────────────────────────────────────────
    report_parser = subparsers.add_parser(
        "report",
        help="Generate time tracking reports",
    )
    report_parser.add_argument(
        "period",
        nargs="?",
        default="daily",
        choices=["daily", "weekly", "monthly"],
        help="Report period (default: daily)",
    )
    report_parser.add_argument(
        "--format", "-f",
        default="markdown",
        choices=["json", "csv", "html", "markdown"],
        help="Output format (default: markdown)",
    )
    report_parser.add_argument(
        "--project", "-p",
        default=None,
        help="Filter by project name",
    )
    report_parser.add_argument(
        "--from",
        dest="from_date",
        default=None,
        help="Start date in YYYY-MM-DD format",
    )
    report_parser.add_argument(
        "--to",
        dest="to_date",
        default=None,
        help="End date in YYYY-MM-DD format",
    )
    report_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: stdout)",
    )

    # ── analyze command ───────────────────────────────────────────────
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run productivity analysis",
    )
    analyze_parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Number of days to analyze (default: 30)",
    )

    # ── git command ───────────────────────────────────────────────────
    git_parser = subparsers.add_parser(
        "git",
        help="Git integration commands",
    )
    git_subparsers = git_parser.add_subparsers(
        dest="git_command",
        help="Git subcommands",
    )

    git_link = git_subparsers.add_parser(
        "link",
        help="Link latest git commit to current time entry",
    )
    git_link.add_argument(
        "--entry", "-e",
        default=None,
        help="Specific entry ID to link (default: active or latest)",
    )

    git_subparsers.add_parser(
        "log",
        help="Show git log with time tracking info",
    )

    # ── config command ────────────────────────────────────────────────
    config_parser = subparsers.add_parser(
        "config",
        help="View or modify configuration",
    )
    config_parser.add_argument(
        "key",
        nargs="?",
        default=None,
        help="Configuration key to view or set",
    )
    config_parser.add_argument(
        "value",
        nargs="?",
        default=None,
        help="New value for the configuration key",
    )
    config_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration to defaults",
    )
    config_parser.add_argument(
        "--list",
        action="store_true",
        dest="list_all",
        help="List all configuration values",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point for TimeForge.

    Parses command-line arguments and dispatches to the appropriate
    handler function.

    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    display = Display()

    try:
        if args.command == "start":
            return _cmd_start(args, display)
        elif args.command == "stop":
            return _cmd_stop(display)
        elif args.command == "pause":
            return _cmd_pause(display)
        elif args.command == "resume":
            return _cmd_resume(display)
        elif args.command == "status":
            return _cmd_status(display)
        elif args.command == "log":
            return _cmd_log(args, display)
        elif args.command == "list":
            return _cmd_list(display)
        elif args.command == "delete":
            return _cmd_delete(args, display)
        elif args.command == "edit":
            return _cmd_edit(args, display)
        elif args.command == "pomo":
            return _cmd_pomo(args, display)
        elif args.command == "report":
            return _cmd_report(args, display)
        elif args.command == "analyze":
            return _cmd_analyze(args, display)
        elif args.command == "git":
            return _cmd_git(args, display)
        elif args.command == "config":
            return _cmd_config(args, display)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        display._print()
        display.warning("Operation cancelled.")
        return 130
    except Exception as e:
        display.error(f"Error: {e}")
        return 1


def _cmd_start(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'start' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.start(args.project, args.description)
    return 0


def _cmd_stop(display: Display) -> int:
    """Handle the 'stop' command.

    Args:
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.stop()
    return 0


def _cmd_pause(display: Display) -> int:
    """Handle the 'pause' command.

    Args:
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.pause()
    return 0


def _cmd_resume(display: Display) -> int:
    """Handle the 'resume' command.

    Args:
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.resume()
    return 0


def _cmd_status(display: Display) -> int:
    """Handle the 'status' command.

    Args:
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.status()
    return 0


def _cmd_log(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'log' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.log(args.date)
    return 0


def _cmd_list(display: Display) -> int:
    """Handle the 'list' command.

    Args:
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    tracker.list_projects()
    return 0


def _cmd_delete(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'delete' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    if tracker.delete_entry(args.id):
        return 0
    return 1


def _cmd_edit(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'edit' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    tracker = TimeTracker()
    if tracker.edit_entry(
        entry_id=args.id,
        project=args.project,
        description=args.description,
        start_time=args.start,
        end_time=args.end,
    ):
        return 0
    return 1


def _cmd_pomo(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'pomo' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    pomo = PomodoroTimer()

    if not args.pomo_command:
        display.info("Usage: timeforge pomo <start|stop|status|config>")
        return 1

    if args.pomo_command == "start":
        pomo.start(args.duration)
    elif args.pomo_command == "stop":
        pomo.stop()
    elif args.pomo_command == "status":
        pomo.status()
    elif args.pomo_command == "config":
        pomo.show_config()
    else:
        display.error(f"Unknown pomodoro command: {args.pomo_command}")
        return 1

    return 0


def _cmd_report(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'report' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    generator = ReportGenerator()

    try:
        report = generator.generate(
            period=args.period,
            format_type=args.format,
            project=args.project,
            from_date=args.from_date,
            to_date=args.to_date,
        )
    except ValueError as e:
        display.error(str(e))
        return 1

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            display.success(f"Report saved to {args.output}")
        except IOError as e:
            display.error(f"Failed to write report: {e}")
            return 1
    else:
        print(report)

    return 0


def _cmd_analyze(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'analyze' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    engine = AnalyticsEngine()
    engine.display_analysis(days=args.days)
    return 0


def _cmd_git(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'git' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    linker = GitLinker()

    if not args.git_command:
        display.info("Usage: timeforge git <link|log>")
        return 1

    if args.git_command == "link":
        if linker.link_commit(entry_id=args.entry):
            return 0
        return 1
    elif args.git_command == "log":
        linker.show_git_log()
        return 0
    else:
        display.error(f"Unknown git command: {args.git_command}")
        return 1


def _cmd_config(args: argparse.Namespace, display: Display) -> int:
    """Handle the 'config' command.

    Args:
        args: Parsed command-line arguments.
        display: Display utility instance.

    Returns:
        Exit code.
    """
    config = Config()

    if args.reset:
        config.reset()
        display.success("Configuration reset to defaults.")
        return 0

    if args.list_all:
        display.header("TimeForge Configuration")
        all_config = config.get_all()
        rows = []
        for key, value in sorted(all_config.items()):
            rows.append([key, str(value)])
        display.table(["Key", "Value"], rows)
        return 0

    if args.key and args.value is not None:
        # Try to convert numeric values
        try:
            typed_value = int(args.value)
        except ValueError:
            try:
                typed_value = float(args.value)
            except ValueError:
                typed_value = args.value

        config.set(args.key, typed_value)
        display.success(f"Set {args.key} = {typed_value}")
        return 0

    if args.key:
        value = config.get(args.key)
        if value is not None:
            display.info(f"{args.key} = {value}")
        else:
            display.error(f"Unknown configuration key: {args.key}")
            return 1
        return 0

    # No arguments - show current config
    display.header("TimeForge Configuration")
    display.info(f"Config file: {config.config_file}")
    display.info("Use 'timeforge config --list' to see all settings.")
    display.info("Use 'timeforge config <key> <value>' to change a setting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
