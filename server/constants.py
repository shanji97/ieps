PAGE_TYPE_HTML = "HTML"
PAGE_TYPE_FRONTIER = "FRONTIER"
PAGE_TYPE_DUPLICATE = "DUPLICATE"
PAGE_TYPE_BINARY = "BINARY"
PAGE_TYPE_ERROR = "ERROR"

DATA_TYPE_PDF = "PDF"
DATA_TYPE_DOC = "DOC"
DATA_TYPE_DOCX = "DOCX"
DATA_TYPE_PPT = "PPT"
DATA_TYPE_PPTX = "PPTX"

PARSE_STATUS_PARSED: str = "PARSED"
PARSE_STATUS_NOT_PARSED: str = "NOT_PARSED"
PARSE_STATUS_PARSING: str = "PARSING"

DEFAULT_CRAWL_DELAY_SECONDS = 5

OLDER_THAN_SECONDS_WHEN_PARSING = 30 * 60

USERNAME = "fri"
PASSWORD = "fri-pass"

TERMINAL_COLORS = [
    "\033[0;31m",  # Red
    "\033[0;32m",  # Green
    "\033[0;33m",  # Yellow
    "\033[0;34m",  # Blue
    "\033[0;35m",  # Magenta
    "\033[0;36m",  # Cyan
    "\033[0;37m",  # White
    "\033[1;31m",  # Bright red
    "\033[1;32m",  # Bright green
    "\033[1;33m",  # Bright yellow
    "\033[1;34m",  # Bright blue
    "\033[1;35m",  # Bright magenta
    "\033[1;36m",  # Bright cyan
    "\033[1;37m",  # Bright white
    "\033[1;30m",  # Gray
    "\033[0;30m",  # Dark gray
]
END_COLOR = '\033[0m'
