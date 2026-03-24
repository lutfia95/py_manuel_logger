from __future__ import annotations

import atexit
import os
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import TextIO


_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_COLORS: dict[str, str] = {
    "debug": "\033[38;5;244m",
    "info": "\033[38;5;39m",
    "success": "\033[38;5;42m",
    "warning": "\033[38;5;214m",
    "error": "\033[38;5;196m",
    "critical": "\033[48;5;196m\033[38;5;231m",
    "banner": "\033[38;5;141m",
}


@dataclass(frozen=True)
class LogStyle:
    use_color: bool = True
    show_time: bool = True
    show_level: bool = True
    stream: object = sys.stderr


class ManuelLogger:
    LEVELS: dict[str, int] = {
        "debug": 10,
        "info": 20,
        "success": 25,
        "warning": 30,
        "error": 40,
        "critical": 50,
    }

    def __init__(
        self,
        name: str = "app",
        *,
        level: str | None = None,
        log_file: str | None = None,
        use_color: bool | None = None,
        show_time: bool = True,
        show_level: bool = True,
        stream: object = sys.stderr,
    ) -> None:
        self.name = name
        self.level = self._normalize_level(level or os.environ.get("MANUEL_LOG_LEVEL", "info"))
        self._file_stream: TextIO | None = self._open_log_file(log_file)

        if use_color is None:
            use_color = self._stream_supports_color(stream)

        self.style = LogStyle(
            use_color=use_color,
            show_time=show_time,
            show_level=show_level,
            stream=stream,
        )

    def _open_log_file(self, log_file: str | None) -> TextIO | None:
        if not log_file:
            return None

        directory = os.path.dirname(log_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        file_stream = open(log_file, "a", encoding="utf-8")
        atexit.register(file_stream.close)
        return file_stream

    def _normalize_level(self, level: str) -> str:
        key = str(level).strip().lower()
        if key not in self.LEVELS:
            valid = ", ".join(self.LEVELS.keys())
            raise ValueError(f"Invalid log level {level!r}. Valid levels: {valid}")
        return key

    def _stream_supports_color(self, stream: object) -> bool:
        if os.environ.get("NO_COLOR"):
            return False

        isatty = getattr(stream, "isatty", None)
        if callable(isatty):
            try:
                return bool(isatty())
            except Exception:
                return False

        return False

    def set_level(self, level: str) -> None:
        self.level = self._normalize_level(level)

    def _should_log(self, level: str) -> bool:
        return self.LEVELS[level] >= self.LEVELS[self.level]

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _colorize(self, text: str, kind: str) -> str:
        if not self.style.use_color:
            return text

        prefix = _COLORS.get(kind, "")
        return f"{prefix}{text}{_RESET}"

    def _format_prefix(self, level: str, *, use_color: bool) -> str:
        parts: list[str] = []

        if self.style.show_time:
            timestamp = self._timestamp()
            parts.append(self._colorize(timestamp, "debug") if use_color else timestamp)

        if self.style.show_level:
            label = level.upper().ljust(8)
            parts.append(self._colorize(label, level) if use_color else label)

        parts.append(self._colorize(self.name, "banner") if use_color else self.name)

        return " | ".join(parts)

    def _emit(self, level: str, message: str) -> None:
        if not self._should_log(level):
            return

        console_prefix = self._format_prefix(level, use_color=self.style.use_color)
        print(f"{console_prefix} | {message}", file=self.style.stream)

        if self._file_stream is not None:
            file_prefix = self._format_prefix(level, use_color=False)
            print(f"{file_prefix} | {message}", file=self._file_stream)
            self._file_stream.flush()

    def debug(self, message: str) -> None:
        self._emit("debug", message)

    def info(self, message: str) -> None:
        self._emit("info", message)

    def success(self, message: str) -> None:
        self._emit("success", message)

    def warning(self, message: str) -> None:
        self._emit("warning", message)

    def error(self, message: str) -> None:
        self._emit("error", message)

    def critical(self, message: str) -> None:
        self._emit("critical", message)

    def banner(self, title: str) -> None:
        line = "═" * max(10, len(title) + 4)
        text = f"{line}\n  {title}\n{line}"
        self._emit("info", self._colorize(text, "banner"))

    def section(self, title: str) -> None:
        self._emit("info", f"{_BOLD}{title}{_RESET}" if self.style.use_color else title)

    def kv(self, key: str, value: object, *, level: str = "info") -> None:
        label = f"{key:<22}"
        text = f"{label}: {value}"
        self._emit(level, text)

    def pair(self, left: str, right: str, *, arrow: str = "->", level: str = "info") -> None:
        self._emit(level, f"{left} {arrow} {right}")

    def missing(self, what: str, value: object) -> None:
        self.warning(f"Missing {what}: {value!r}")

    def exception(self, message: str, exc: BaseException) -> None:
        self.error(f"{message}: {exc.__class__.__name__}: {exc}")
        details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).rstrip()
        if details:
            self._emit("error", details)
