"""Application-wide constants."""
from typing import Final

# File Processing Constants
MAX_FILE_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10MB
MAX_FILE_SIZE_MB: Final[float] = 10.0

# Job Processing Constants
ESTIMATED_TIME_PER_KEYWORD_PER_WEBSITE_SECONDS: Final[int] = 5
CSV_PREVIEW_MAX_ROWS: Final[int] = 10

# API Constants
DEFAULT_JOB_LIST_LIMIT: Final[int] = 20
MAX_JOB_LIST_LIMIT: Final[int] = 100

