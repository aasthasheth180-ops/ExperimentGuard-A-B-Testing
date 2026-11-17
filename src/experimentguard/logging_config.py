
import logging
import os


def configure_logging() -> None:
    """Configure application-level logging."""

    log_level_name = os.getenv(
        "LOG_LEVEL", "INFO"
    ).upper()

    log_level = getattr(
        logging,
        log_level_name,
        None,
    )

    if not isinstance(log_level, int):
        raise ValueError(
            f"Invalid LOG_LEVEL: {log_level_name}"
        )

    logger = logging.getLogger("experimentguard")

    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
