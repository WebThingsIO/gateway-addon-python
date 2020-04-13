"""High-level Outlet base class implementation."""

from __future__ import print_function
import functools


print = functools.partial(print, flush=True)


class Outlet:
    """An Outlet represents a notification channel for a Notifier."""

    def __init__(self, notifier, _id):
        """
        Initialize the object.

        notifier -- the Notifier managing this outlet
        _id -- the outlet's individual ID
        """
        self.notifier = notifier
        self.id = str(_id)
        self.name = ''

    def as_dict(self):
        """
        Get the outlet state as a dictionary.

        Returns the state as a dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
        }

    def get_id(self):
        """
        Get the ID of the outlet.

        Returns the ID as a string.
        """
        return self.id

    def get_name(self):
        """
        Get the name of the outlet.

        Returns the name as a string.
        """
        return self.name

    def notify(self, title, message, level):
        """
        Notify the user.

        title -- title of notification
        message -- message of notification
        level -- alert level
        """
        if self.notifier.verbose:
            print('Outlet: {} notify("{}", "{}", {})'
                  .format(self.name, title, message, level))
