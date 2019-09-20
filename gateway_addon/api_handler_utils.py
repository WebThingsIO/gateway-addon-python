"""Utility functions and classes for API handlers."""

import pprint


class APIRequest:
    """Class which holds an API request."""

    def __init__(self, **kwargs):
        """Initialize the object."""
        self.method = kwargs.get('method', None)
        self.path = kwargs.get('path', None)
        self.query = kwargs.get('query', None)
        self.body = kwargs.get('body', None)

    def __str__(self):
        """Format this object as a string."""
        return pprint.pformat({
            'method': self.method,
            'path': self.path,
            'query': self.query,
            'body': self.body,
        })


class APIResponse:
    """Class which holds an API response."""

    def __init__(self, **kwargs):
        """Initialize the object."""
        self.status = kwargs.get('status', None)
        if self.status is None:
            self.status = 500
            return

        self.content_type = kwargs.get('content_type', None)
        if self.content_type is not None and \
                type(self.content_type) is not str:
            self.content_type = str(self.content_type)

        self.content = kwargs.get('content', None)
        if self.content is not None and type(self.content) is not str:
            self.content = str(self.content)

    def __str__(self):
        """Format this object as a string."""
        return pprint.pformat({
            'status': self.status,
            'content_type': self.content_type,
            'content': self.content,
        })

    def to_json(self):
        """Return JSON representation of this object for IPC."""
        return {
            'status': self.status,
            'contentType': self.content_type,
            'content': self.content,
        }
