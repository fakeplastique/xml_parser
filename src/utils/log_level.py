from enum import Enum


class LogLevel(Enum):
    """
    Enumeration for log event importance levels

    - FILTERING: Filtering operations
    - TRANSFORMATION: Transformation operations
    - SAVING: Saving operations
    """
    FILTERING = "Фільтрація"
    TRANSFORMATION = "Трансформація"
    SAVING = "Збереження"

    def __str__(self) -> str:
        """Return the Ukrainian name of the log level"""
        return self.value
