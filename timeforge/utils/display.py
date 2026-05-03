"""Terminal display utilities for TimeForge.

Provides colored output, table rendering, progress bars, and bar charts
using only ANSI escape codes (no external dependencies).
"""

import os
import shutil
import sys
import time
from typing import Any, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output.

    Provides static methods for wrapping text in ANSI color codes.
    Automatically disables colors when output is not a TTY.
    """

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    _enabled: bool = True

    @classmethod
    def disable(cls) -> None:
        """Disable colored output globally."""
        cls._enabled = False

    @classmethod
    def enable(cls) -> None:
        """Enable colored output globally."""
        cls._enabled = True

    @classmethod
    def _wrap(cls, text: str, code: str) -> str:
        """Wrap text in an ANSI escape code.

        Args:
            text: The text to wrap.
            code: The ANSI escape code.

        Returns:
            Text wrapped in ANSI codes, or plain text if disabled.
        """
        if not cls._enabled:
            return text
        return f"{code}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Return text in bold.

        Args:
            text: The text to format.

        Returns:
            Bold formatted text.
        """
        return cls._wrap(text, cls.BOLD)

    @classmethod
    def dim(cls, text: str) -> str:
        """Return text in dim (faint) style.

        Args:
            text: The text to format.

        Returns:
            Dim formatted text.
        """
        return cls._wrap(text, cls.DIM)

    @classmethod
    def red(cls, text: str) -> str:
        """Return text in red.

        Args:
            text: The text to format.

        Returns:
            Red colored text.
        """
        return cls._wrap(text, cls.RED)

    @classmethod
    def green(cls, text: str) -> str:
        """Return text in green.

        Args:
            text: The text to format.

        Returns:
            Green colored text.
        """
        return cls._wrap(text, cls.GREEN)

    @classmethod
    def yellow(cls, text: str) -> str:
        """Return text in yellow.

        Args:
            text: The text to format.

        Returns:
            Yellow colored text.
        """
        return cls._wrap(text, cls.YELLOW)

    @classmethod
    def blue(cls, text: str) -> str:
        """Return text in blue.

        Args:
            text: The text to format.

        Returns:
            Blue colored text.
        """
        return cls._wrap(text, cls.BLUE)

    @classmethod
    def magenta(cls, text: str) -> str:
        """Return text in magenta.

        Args:
            text: The text to format.

        Returns:
            Magenta colored text.
        """
        return cls._wrap(text, cls.MAGENTA)

    @classmethod
    def cyan(cls, text: str) -> str:
        """Return text in cyan.

        Args:
            text: The text to format.

        Returns:
            Cyan colored text.
        """
        return cls._wrap(text, cls.CYAN)

    @classmethod
    def bright_cyan(cls, text: str) -> str:
        """Return text in bright cyan.

        Args:
            text: The text to format.

        Returns:
            Bright cyan colored text.
        """
        return cls._wrap(text, cls.BRIGHT_CYAN)


class Display:
    """Terminal display utility for TimeForge.

    Provides methods for formatted output including tables, progress bars,
    bar charts, and colored messages. Automatically adapts to terminal width.

    Attributes:
        width: Detected terminal width (defaults to 80).
    """

    def __init__(self, width: Optional[int] = None):
        """Initialize the Display utility.

        Args:
            width: Custom terminal width. Auto-detected if None.
        """
        self.width = width or self._detect_terminal_width()

    @staticmethod
    def _detect_terminal_width() -> int:
        """Detect the terminal width.

        Returns:
            Terminal width in columns, or 80 if detection fails.
        """
        try:
            return shutil.get_terminal_size().columns
        except (AttributeError, ValueError):
            return 80

    def _print(self, text: str = "") -> None:
        """Print text to stdout.

        Args:
            text: The text to print.
        """
        print(text)

    def _print_err(self, text: str = "") -> None:
        """Print text to stderr.

        Args:
            text: The text to print.
        """
        print(text, file=sys.stderr)

    # ── Message methods ───────────────────────────────────────────────

    def info(self, message: str) -> None:
        """Display an informational message.

        Args:
            message: The message to display.
        """
        self._print(f"{Colors.cyan('>>')} {message}")

    def success(self, message: str) -> None:
        """Display a success message.

        Args:
            message: The message to display.
        """
        self._print(f"{Colors.green('>>')} {message}")

    def warning(self, message: str) -> None:
        """Display a warning message.

        Args:
            message: The message to display.
        """
        self._print_err(f"{Colors.yellow('!!')} {message}")

    def error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: The message to display.
        """
        self._print_err(f"{Colors.red('!!')} {message}")

    def header(self, title: str) -> None:
        """Display a section header.

        Args:
            title: The header title.
        """
        self._print()
        self._print(f"{Colors.bold(Colors.bright_cyan(title))}")
        self._print(Colors.dim("=" * min(len(title), self.width)))
        self._print()

    # ── Table rendering ───────────────────────────────────────────────

    def table(
        self,
        headers: List[str],
        rows: List[List[str]],
        padding: int = 2,
    ) -> None:
        """Render a formatted table in the terminal.

        Automatically calculates column widths based on content.

        Args:
            headers: List of column header strings.
            rows: List of rows, each row is a list of cell strings.
            padding: Horizontal padding within each cell.
        """
        if not rows:
            return

        # Calculate column widths
        num_cols = len(headers)
        col_widths = [len(h) for h in headers]

        for row in rows:
            for i, cell in enumerate(row):
                if i < num_cols:
                    # Strip ANSI codes for width calculation
                    clean_cell = self._strip_ansi(cell)
                    col_widths[i] = max(col_widths[i], len(clean_cell))

        # Limit total width
        total_width = sum(col_widths) + padding * 2 * num_cols + (num_cols - 1) * 3
        if total_width > self.width and num_cols > 1:
            # Reduce the widest column
            excess = total_width - self.width
            max_col_idx = col_widths.index(max(col_widths))
            col_widths[max_col_idx] = max(col_widths[max_col_idx] - excess, len(headers[max_col_idx]))

        # Build format string
        col_formats = []
        for w in col_widths:
            col_formats.append(f"{{:<{w}}}")
        format_str = " | ".join(col_formats)

        # Print header
        header_line = format_str.format(*headers)
        self._print(Colors.bold(header_line))

        # Print separator
        separator_parts = []
        for w in col_widths:
            separator_parts.append("-" * w)
        self._print(Colors.dim("-+-".join(separator_parts)))

        # Print rows
        for row in rows:
            # Pad row to match number of columns
            padded_row = list(row) + [""] * (num_cols - len(row))
            line = format_str.format(*padded_row[:num_cols])
            self._print(line)

        self._print()

    # ── Progress bar ──────────────────────────────────────────────────

    def progress_bar(
        self,
        current: float,
        total: float,
        width: Optional[int] = None,
        label: str = "",
        fill_char: str = "\u2588",
        empty_char: str = "\u2591",
    ) -> str:
        """Generate a progress bar string.

        Args:
            current: Current progress value.
            total: Total value representing 100%.
            width: Bar width in characters. Defaults to 30.
            label: Optional label to prepend.
            fill_char: Character for filled portion.
            empty_char: Character for empty portion.

        Returns:
            The formatted progress bar string.
        """
        bar_width = width or 30
        if total <= 0:
            percent = 0.0
        else:
            percent = min(current / total, 1.0)

        filled = int(bar_width * percent)
        empty = bar_width - filled

        bar = fill_char * filled + empty_char * empty
        percent_str = f"{percent * 100:.1f}%"

        if label:
            return f"{label} [{bar}] {percent_str}"
        return f"[{bar}] {percent_str}"

    def progress_bar_inline(
        self,
        current: float,
        total: float,
        width: Optional[int] = None,
        label: str = "",
    ) -> None:
        """Print a progress bar that updates on the same line.

        Args:
            current: Current progress value.
            total: Total value representing 100%.
            width: Bar width in characters.
            label: Optional label to prepend.
        """
        bar_str = self.progress_bar(current, total, width, label)
        sys.stdout.write(f"\r{bar_str}")
        sys.stdout.flush()

    # ── Bar chart ─────────────────────────────────────────────────────

    def bar_chart(
        self,
        data: List[Tuple[str, float]],
        max_bar_width: Optional[int] = None,
        title: str = "",
        show_values: bool = True,
    ) -> None:
        """Render a horizontal bar chart using Unicode block characters.

        Args:
            data: List of (label, value) tuples.
            max_bar_width: Maximum bar width in characters.
            title: Optional chart title.
            show_values: Whether to show numeric values.
        """
        if not data:
            return

        if title:
            self._print(Colors.bold(title))
            self._print()

        max_value = max(v for _, v in data) if data else 1
        if max_value <= 0:
            max_value = 1

        bar_width = max_bar_width or min(40, self.width - 30)

        # Calculate max label length
        max_label_len = max(len(label) for label, _ in data)

        for label, value in data:
            # Calculate bar length
            bar_len = int((value / max_value) * bar_width)
            if bar_len == 0 and value > 0:
                bar_len = 1

            # Use different block characters for a gradient effect
            bar = self._create_gradient_bar(bar_len, bar_width)

            # Format label
            label_str = f"{label:<{max_label_len}}"

            if show_values:
                value_str = f" {value:.1f}"
            else:
                value_str = ""

            self._print(f"  {label_str} {Colors.cyan(bar)}{value_str}")

        self._print()

    def _create_gradient_bar(self, filled: int, total: int) -> str:
        """Create a gradient bar using Unicode block characters.

        Uses different block characters to create a visual gradient:
        filled (\u2588), dark shade (\u2593), medium (\u2592), light (\u2591).

        Args:
            filled: Number of filled positions.
            total: Total bar width.

        Returns:
            The gradient bar string.
        """
        if filled >= total:
            return "\u2588" * total

        bar = "\u2588" * filled
        remaining = total - filled

        if remaining >= 3:
            bar += "\u2593\u2592\u2591"
            remaining -= 3
        elif remaining >= 2:
            bar += "\u2593\u2592"
            remaining -= 2
        elif remaining >= 1:
            bar += "\u2593"
            remaining -= 1

        bar += " " * remaining
        return bar

    # ── Completion animation ──────────────────────────────────────────

    def completion_animation(self, message: str = "Done!") -> None:
        """Display a simple completion animation in the terminal.

        Shows a brief character animation followed by the message.

        Args:
            message: The completion message to display.
        """
        frames = [
            Colors.green("[====>") + " " + message,
            Colors.green("[=====>") + " " + message,
            Colors.green(" [====>") + " " + message,
        ]
        for frame in frames:
            sys.stdout.write(f"\r  {frame}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r")
        sys.stdout.flush()
        self._print(f"  {Colors.green(Colors.bold(message))}")

    # ── Utility methods ───────────────────────────────────────────────

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape codes from a string.

        Args:
            text: The text to strip.

        Returns:
            Plain text without ANSI codes.
        """
        import re
        ansi_escape = re.compile(r"\033\[[0-9;]*m")
        return ansi_escape.sub("", text)

    def clear_line(self) -> None:
        """Clear the current terminal line."""
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
