"""High-level Notifier base class implementation."""

from __future__ import print_function
import functools

from .addon_manager_proxy import AddonManagerProxy


print = functools.partial(print, flush=True)


class Notifier:
    """A Notifier represents a way of sending alerts to a user."""

    def __init__(self, _id, package_name, verbose=False):
        """
        Initialize the object.

        As part of initialization, a connection is established between the
        notifier and the Gateway via nanomsg IPC.

        _id -- the notifier's individual ID
        package_name -- the notifier's package name
        verbose -- whether or not to enable verbose logging
        """
        self.id = _id
        self.package_name = package_name
        self.outlets = {}

        # We assume that the notifier is ready right away. If, for some reason,
        # a particular notifier needs some time, then it should set ready to
        # False in its constructor.
        self.ready = True

        self.manager_proxy = \
            AddonManagerProxy(self.package_name, verbose=verbose)
        self.manager_proxy.add_notifier(self)

        self.gateway_version = self.manager_proxy.gateway_version
        self.user_profile = self.manager_proxy.user_profile
        self.preferences = self.manager_proxy.preferences

    def proxy_running(self):
        """Return boolean indicating whether or not the proxy is running."""
        return self.manager_proxy.running

    def close_proxy(self):
        """Close the manager proxy."""
        self.manager_proxy.close()

    def send_error(self, message):
        """
        Send an error notification.

        message -- error message
        """
        self.manager_proxy.send_error(message)

    def dump(self):
        """Dump the state of the notifier to the log."""
        print('Notifier:', self.name, '- dump() not implemented')

    def get_id(self):
        """
        Get the ID of the notifier.

        Returns the ID as a string.
        """
        return self.id

    def get_package_name(self):
        """
        Get the package name of the notifier.

        Returns the package name as a string.
        """
        return self.package_name

    def get_outlet(self, outlet_id):
        """
        Get the outlet with the given ID.

        outlet_id -- ID of outlet to retrieve

        Returns an Outlet object, if found, else None.
        """
        return self.outlets.get(outlet_id, None)

    def get_outlets(self):
        """
        Get all the outlets managed by this notifier.

        Returns a dictionary of outlet_id -> Outlet.
        """
        return self.outlets

    def get_name(self):
        """
        Get the name of this notifier.

        Returns the name as a string.
        """
        return self.name

    def is_ready(self):
        """
        Get the ready state of this notifier.

        Returns the ready state as a boolean.
        """
        return self.ready

    def as_dict(self):
        """
        Get the notifier state as a dictionary.

        Returns the state as a dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'ready': self.ready,
        }

    def handle_outlet_added(self, outlet):
        """
        Notify the Gateway that a new outlet is being managed by this notifier.

        outlet -- Outlet object
        """
        self.outlets[outlet.id] = outlet
        self.manager_proxy.handle_outlet_added(outlet)

    def handle_outlet_removed(self, outlet):
        """
        Notify the Gateway that an outlet has been removed.

        outlet -- Outlet object
        """
        if outlet.id in self.outlets:
            del self.outlets[outlet.id]

        self.manager_proxy.handle_outlet_removed(outlet)

    def unload(self):
        """Perform any necessary cleanup before notifier is shut down."""
        print('Notifier:', self.name, 'unloaded')
