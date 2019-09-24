"""High-level API Handler base class implementation."""

from __future__ import print_function
import functools

from .addon_manager_proxy import AddonManagerProxy
from .api_handler_utils import APIResponse


print = functools.partial(print, flush=True)


class APIHandler:
    """An API handler represents a way of extending the gateway's REST API."""

    def __init__(self, package_name, verbose=False):
        """
        Initialize the object.

        As part of initialization, a connection is established between the
        handler and the Gateway via nanomsg IPC.

        package_name -- the handler's package name
        verbose -- whether or not to enable verbose logging
        """
        self.package_name = package_name

        self.manager_proxy = \
            AddonManagerProxy(self.package_name, verbose=verbose)
        self.manager_proxy.add_api_handler(self)

        self.user_profile = self.manager_proxy.user_profile

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

    def get_package_name(self):
        """
        Get the package name of the handler.

        Returns the package name as a string.
        """
        return self.package_name

    def handle_request(self, request):
        """
        Handle a new API request for this handler.

        request -- APIRequest object
        """
        print('New API request for {}: {}'.format(self.package_name, request))
        return APIResponse(status=404)

    def unload(self):
        """Perform any necessary cleanup before handler is shut down."""
        print('API Handler:', self.package_name, 'unloaded')
