"""
Text Utilities

Functions for text post-processing and formatting.
"""


def postprocess(text: str, remove_trailing_period: bool, add_trailing_space: bool) -> str:
    """
    Post-process transcribed text.

    Args:
        text: Input text
        remove_trailing_period: Whether to remove trailing period
        add_trailing_space: Whether to add trailing space

    Returns:
        Processed text
    """
    t = (text or "").strip()

    if remove_trailing_period and t.endswith("."):
        t = t[:-1].rstrip()

    if add_trailing_space:
        t += " "

    return t
