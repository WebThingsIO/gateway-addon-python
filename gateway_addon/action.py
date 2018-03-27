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
        return {
            'id': self.id,
            'name': self.name,
            'input': self.input,
            'status': self.status,
            'timeRequested': self.time_requested,
            'timeCompleted': self.time_completed,
        }

    def get_id(self):
        """Get this action's ID."""
        return self.id

    def get_name(self):
        """Get this action's name."""
        return self.name

    def get_status(self):
        """Get this action's status."""
        return self.status

    def get_device(self):
        """Get the device associated with this action."""
        return self.device

    def get_time_requested(self):
        """Get the time the action was requested."""
        return self.time_requested

    def get_time_completed(self):
        """Get the time the action was completed."""
        return self.time_completed

    def get_input(self):
        """Get the inputs for this action."""
        return self.input

    def start(self):
        """Start performing the action."""
        self.status = 'pending'
        self.device.action_notify(self)

    def finish(self):
        """Finish performing the action."""
        self.status = 'completed'
        self.time_completed = timestamp()
        self.device.action_notify(self)
