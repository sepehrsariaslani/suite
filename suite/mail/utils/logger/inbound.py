from suite.mail.utils.logger.base import EventLogger


class InboundLogger(EventLogger):
	"""Structured event logger for inbound mail operations ("suite.mail.inbound")."""

	logger_name = "suite.mail.inbound"
	config_prefix = "inbound"


def get_inbound_logger(ctx: dict | None = None) -> InboundLogger:
	"""Returns a structured event logger for inbound mail operations.

	The returned `InboundLogger` is bound to `ctx` (by reference); mutating that
	same dict between log calls is reflected in subsequent records.
	"""

	return InboundLogger(ctx)
