"""Helpers for one-line text previews shared by the list screens."""

DESCRIPTION_PREVIEW_LENGTH = 90


def shorten_description(description: str, limit: int = DESCRIPTION_PREVIEW_LENGTH) -> str:
    """Flatten a description to a single line and truncate it to the given limit."""
    single_line = " ".join(description.split())

    if len(single_line) <= limit:
        return single_line

    return single_line[: limit - 1].rstrip() + "…"
