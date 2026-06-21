from suite.mail.utils.logger.base import EventLogger


class StorageLogger(EventLogger):
	"""Structured event logger for mail storage operations ("suite.mail.storage")."""

	logger_name = "suite.mail.storage"
	config_prefix = "storage"


def get_storage_logger(ctx: dict | None = None) -> StorageLogger:
	"""Returns a structured event logger for mail storage operations.

	The returned `StorageLogger` is bound to `ctx` (by reference); mutating that
	same dict between log calls is reflected in subsequent records.
	"""

	return StorageLogger(ctx)
