"""High-level Action base class implementation."""

from .utils import timestamp


class Action:
    """An Action represents an individual action on a device."""

    def __init__(self, id_, device, name, input_):
        """
        Initialize the object.

        id_ ID of this action
        device -- the device this action belongs to
        name -- name of the action
        input_ -- any action inputs
        """
        self.id = id_
        self.device = device
        self.name = name
        self.input = input_
        self.status = 'created'
        self.time_requested = timestamp()
        self.time_completed = None

    def as_action_description(self):
        """
        Get the action description.

        Returns a dictionary describing the action.
        """
        description = {
            'name': self.name,
            'timeRequested': self.time_requested,
            'status': self.status,
        }

        if self.input is not None:
            description['input'] = self.input

        if self.time_completed is not None:
            description['timeCompleted'] = self.time_completed

        return description

    def as_dict(self):
        """
        Get the action description.

        Returns a dictionary describing the action.
        """
        d = self.as_action_description()
        d['id'] = self.id
        return d

    def start(self):
        """Start performing the action."""
        self.status = 'pending'
        self.device.action_notify(self)

    def finish(self):
        """Finish performing the action."""
        self.status = 'completed'
        self.time_completed = timestamp()
        self.device.action_notify(self)
