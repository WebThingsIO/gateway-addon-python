"""Utility functions."""

import datetime


def timestamp():
    """
    Get the current time.

    Returns the current time in the form YYYY-mm-ddTHH:MM:SS+00:00
    """
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
