import logging
from logging.handlers import RotatingFileHandler

from lupix_studio.core.paths import ensure_directories, logs_dir


def configure_logging() -> None:
    """Configura logging do Lupix Studio."""
    ensure_directories()

    logger = logging.getLogger("lupix_studio")

    if logger.handlers:
        return

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = RotatingFileHandler(
        logs_dir() / "lupix.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)