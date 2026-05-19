class CheckFailed(Exception):
    """Raised by jktz.validation.* check() functions when a check fails.

    The exception message is the multi-line error block that should be
    printed to the user, matching the format of the legacy bash scripts.
    """
