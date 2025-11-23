import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from .log_level import LogLevel


class Logger:

    _instance: Optional['Logger'] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, log_file: str = "application.log") -> 'Logger':
        """
        Create or return the singleton instance

        This method ensures that only one instance of Logger exists.
        Uses double-checked locking pattern for thread safety.

        Args:
            log_file: Path to the log file (default: "application.log")

        Returns:
            The singleton Logger instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_file: str = "application.log") -> None:
        """
        Initialize the logger
        
        Args:
            log_file: Path to the log file (default: "application.log")
        """
        # Ensure initialization happens only once
        if Logger._initialized:
            return

        with Logger._lock:
            if Logger._initialized:
                return

            self._log_file_path = Path(log_file)
            self._ensure_log_file_exists()
            Logger._initialized = True

    def _ensure_log_file_exists(self) -> None:
        """
        Create the log file if it doesn't exist

        Creates parent directories if needed.
        """
        self._log_file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self._log_file_path.exists():
            self._log_file_path.touch()

    def _format_timestamp(self) -> str:
        """
        Get current timestamp in the required format

        Returns:
            Formatted timestamp string (dd.mm.yyyy HH:MM:SS)

        """
        now = datetime.now()
        return now.strftime("%d.%m.%Y %H:%M:%S")

    def log(self, level: LogLevel, message: str) -> None:
        """
        Log an event with timestamp and importance level

        Writes event to the log file in the format:
        DD.MM.YYYY HH:MM:SS Level. Message

        Args:
            level: Event importance level (LogLevel enum)
            message: Descriptive message about the event

        Thread-safe: Multiple threads can safely call this method concurrently.
        """
        timestamp = self._format_timestamp()
        log_entry = f"{timestamp} {level}. {message}\n"

        with Logger._lock:
            with open(self._log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)

    def log_filtering(self, message: str) -> None:
        """
        Convenience method for logging filtering events

        Args:
            message: Descriptive message about the filtering operation

        """
        self.log(LogLevel.FILTERING, message)

    def log_transformation(self, message: str) -> None:
        """
        Convenience method for logging transformation events

        Args:
            message: Descriptive message about the transformation operation
        """
        self.log(LogLevel.TRANSFORMATION, message)

    def log_saving(self, message: str) -> None:
        """
        Convenience method for logging saving events

        Args:
            message: Descriptive message about the saving operation
        """
        self.log(LogLevel.SAVING, message)

    def get_log_file_path(self) -> Path:
        """
        Get the path to the log file

        Returns:
            Path object pointing to the log file
        """
        return self._log_file_path

    def clear_log(self) -> None:
        """
        Clear all contents of the log file
        """
        with Logger._lock:
            with open(self._log_file_path, 'w', encoding='utf-8') as f:
                f.write("")

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False
