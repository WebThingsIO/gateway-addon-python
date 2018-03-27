"""High-level Event base class implementation."""

from .utils import timestamp


class Event:
    """An Event represents an individual event from a device."""

    def __init__(self, device, name, data=None):
        """
        Initialize the object.

        device -- device this event belongs to
        name -- name of the event
        data -- data associated with the event
        """
        self.device = device
        self.name = name
        self.data = data
        self.timestamp = timestamp()

    def as_event_description(self):
        """
        Get the event description.

        Returns a dictionary describing the event.
        """
        description = {
            'name': self.name,
            'timestamp': self.timestamp,
        }

        if self.data is not None:
            description['data'] = self.data

        return description

    def as_dict(self):
        """
        Get the event description.

        Returns a dictionary describing the event.
        """
        return {
            'name': self.name,
            'data': self.data,
            'timestamp': self.timestamp,
        }
