"""High-level Adapter base class implementation."""

from __future__ import print_function
import functools

from .addon_manager_proxy import AddonManagerProxy
from .errors import SetCredentialsError, SetPinError


print = functools.partial(print, flush=True)


class Adapter:
    """An Adapter represents a way of communicating with a set of devices."""

    def __init__(self, _id, package_name, verbose=False):
        """
        Initialize the object.

        As part of initialization, a connection is established between the
        adapter and the Gateway via nanomsg IPC.

        _id -- the adapter's individual ID
        package_name -- the adapter's package name
        verbose -- whether or not to enable verbose logging
        """
        self.id = _id
        self.package_name = package_name
        self.devices = {}
        self.actions = {}

        # We assume that the adapter is ready right away. If, for some reason,
        # a particular adapter needs some time, then it should set ready to
        # False in its constructor.
        self.ready = True

        self.manager_proxy = AddonManagerProxy(self.id, verbose=verbose)
        self.manager_proxy.add_adapter(self)

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

    def dump(self):
        """Dump the state of the adapter to the log."""
        print('Adapter:', self.name, '- dump() not implemented')

    def get_id(self):
        """
        Get the ID of the adapter.

        Returns the ID as a string.
        """
        return self.id

    def get_package_name(self):
        """
        Get the package name of the adapter.

        Returns the package name as a string.
        """
        return self.package_name

    def get_device(self, device_id):
        """
        Get the device with the given ID.

        device_id -- ID of device to retrieve

        Returns a Device object, if found, else None.
        """
        return self.devices.get(device_id, None)

    def get_devices(self):
        """
        Get all the devices managed by this adapter.

        Returns a dictionary of device_id -> Device.
        """
        return self.devices

    def get_name(self):
        """
        Get the name of this adapter.

        Returns the name as a string.
        """
        return self.name

    def is_ready(self):
        """
        Get the ready state of this adapter.

        Returns the ready state as a boolean.
        """
        return self.ready

    def as_dict(self):
        """
        Get the adapter state as a dictionary.

        Returns the state as a dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'ready': self.ready,
        }

    def handle_device_added(self, device):
        """
        Notify the Gateway that a new device is being managed by this adapter.

        device -- Device object
        """
        self.devices[device.id] = device
        self.manager_proxy.handle_device_added(device)

    def handle_device_removed(self, device):
        """
        Notify the Gateway that a device has been removed.

        device -- Device object
        """
        if device.id in self.devices:
            del self.devices[device.id]

        self.manager_proxy.handle_device_removed(device)

    def start_pairing(self, timeout):
        """
        Start the pairing process.

        timeout -- Timeout in seconds at which to quit pairing
        """
        print('Adapter:', self.name, 'id', self.id, 'pairing started')

    def send_pairing_prompt(self, prompt, url=None, device=None):
        """
        Send a prompt to the UI notifying the user to take some action.

        prompt -- The prompt to send
        url -- URL to site with further explanation or troubleshooting info
        device -- Device the prompt is associated with
        """
        self.manager_proxy.send_pairing_prompt(self, prompt, url, device)

    def send_unpairing_prompt(self, prompt, url=None, device=None):
        """
        Send a prompt to the UI notifying the user to take some action.

        prompt -- The prompt to send
        url -- URL to site with further explanation or troubleshooting info
        device -- Device the prompt is associated with
        """
        self.manager_proxy.send_unpairing_prompt(self, prompt, url, device)

    def cancel_pairing(self):
        """Cancel the pairing process."""
        print('Adapter:', self.name, 'id', self.id, 'pairing cancelled')

    def remove_thing(self, device_id):
        """
        Unpair a device with the adapter.

        device_id -- ID of device to unpair
        """
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'remove_thing(' + device.id + ')')

            self.handle_device_removed(device)

    def cancel_remove_thing(self, device_id):
        """
        Cancel unpairing of a device.

        device_id -- ID of device to cancel unpairing with
        """
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'cancel_remove_thing(' + device.id + ')')

    def unload(self):
        """Perform any necessary cleanup before adapter is shut down."""
        print('Adapter:', self.name, 'unloaded')

    def set_pin(self, device_id, pin):
        """
        Set the PIN for the given device.

        device_id -- ID of device
        pin -- PIN to set
        """
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'set_pin(' + device.id + ', ' + pin + ')')
        else:
            raise SetPinError('Device not found')

    def set_credentials(self, device_id, username, password):
        """
        Set the username and password for the given device.

        device_id -- ID of device
        username -- Username to set
        password -- Password to set
        """
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'set_credentials(' + device.id + ', ' + username + ', ' +
                  password + ')')
        else:
            raise SetCredentialsError('Device not found')
