"""Proxy for sending messages between the Gateway and an add-on."""

import json
import threading


class AddonManagerProxy:
    """
    Proxy for communicating with the Gateway's AddonManager.

    This proxy interprets all of the required incoming message types that need
    to be handled by add-ons and sends back responses as appropriate.
    """

    def __init__(self, socket, plugin_id, verbose=False):
        """
        Initialize the object.

        socket -- the IPC socket
        plugin_id -- ID of this plugin
        verbose -- whether or not to enable verbose logging
        """
        self.adapter = None
        self.socket = socket
        self.plugin_id = plugin_id
        self.verbose = verbose
        self.running = True
        self.thread = threading.Thread(target=self.recv)
        self.thread.start()

    def close(self):
        """Close the proxy."""
        self.running = False
        self.socket.close()

    def add_adapter(self, adapter):
        """
        Send a notification that an adapter has been added.

        adapter -- the Adapter that was added
        """
        if self.verbose:
            print('AddonManagerProxy: add_adapter:', adapter.id)

        self.adapter = adapter
        self.send('addAdapter', {
            'adapterId': adapter.id,
            'name': adapter.name
        })

    def handle_device_added(self, device):
        """
        Send a notification that a new device has been added.

        device -- the Device that was added
        """
        if self.verbose:
            print('AddonManagerProxy: handle_device_added:', device.id)

        device_dict = device.as_dict()
        device_dict['adapterId'] = device.adapter.id
        self.send('handleDeviceAdded', device_dict)

    def handle_device_removed(self, device):
        """
        Send a notification that a managed device was removed.

        device -- the Device that was removed
        """
        if self.verbose:
            print('AddonManagerProxy: handle_device_removed:', device.id)

        self.send('handleDeviceRemoved', {
            'adapterId': device.adapter.id,
            'id': device.id,
        })

    def send_property_changed_notification(self, prop):
        """
        Send a notification that a device property changed.

        prop -- the Property that changed
        """
        self.send('propertyChanged', {
            'adapterId': prop.device.adapter.id,
            'deviceId': prop.device.id,
            'property': prop.as_dict(),
        })

    def send(self, msg_type, data):
        """
        Send a message through the IPC socket.

        msg_type -- the message type
        data -- the data to send, as a dictionary
        """
        if data is None:
            data = {}

        data['pluginId'] = self.plugin_id

        self.socket.send(json.dumps({
            'messageType': msg_type,
            'data': data,
        }))

    def recv(self):
        """Read a message from the IPC socket."""
        while self.running:
            msg = self.socket.recv()

            if self.verbose:
                print('AddonMangerProxy: recv:', msg)

            if not msg:
                break

            if not self.adapter:
                print('AddonManagerProxy: No adapter added yet, ignoring '
                      'message.')
                continue

            try:
                msg = json.loads(msg)
            except ValueError:
                print('AddonManagerProxy: Error parsing message as JSON')
                continue

            if 'messageType' not in msg:
                print('AddonManagerProxy: Invalid message')
                continue

            msg_type = msg['messageType']

            # High-level adapter messages
            if msg_type == 'startPairing':
                self.adapter.start_pairing(msg['data']['timeout'])
                continue

            if msg_type == 'cancelPairing':
                self.adapter.cancel_pairing()
                continue

            if msg_type == 'unloadAdapter':
                self.adapter.unload()
                self.send('adapterUnloaded', {'adapterId', self.adapter.id})
                continue

            if msg_type == 'unloadPlugin':
                self.send('pluginUnloaded', {})
                continue

            # All messages from here on are assumed to require a valid deviceId
            if 'data' not in msg or 'deviceId' not in msg['data']:
                print('AddonManagerProxy: No deviceId present in message, '
                      'ignoring.')
                continue

            device_id = msg['data']['device_id']
            if msg_type == 'removeThing':
                self.adapter.remove_thing(device_id)
                continue

            if msg_type == 'cancelRemoveThing':
                self.adapter.cancel_remove_thing(device_id)
                continue

            if msg_type == 'setProperty':
                dev = self.adapter.get_device(device_id)
                if dev:
                    prop = dev.get_property(msg['data']['propertyName'])
                    if prop:
                        prop.set_value(msg['data']['propertyValue'])
                        continue
