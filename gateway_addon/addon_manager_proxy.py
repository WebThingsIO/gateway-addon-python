"""Proxy for sending messages between the Gateway and an add-on."""

from __future__ import print_function
from nnpy.errors import NNError
import functools
import json
import threading
import time

from .ipc import IpcClient
from .errors import (ActionError, NotifyError, PropertyError,
                     SetCredentialsError, SetPinError)

print = functools.partial(print, flush=True)


class AddonManagerProxy:
    """
    Proxy for communicating with the Gateway's AddonManager.

    This proxy interprets all of the required incoming message types that need
    to be handled by add-ons and sends back responses as appropriate.
    """

    def __init__(self, plugin_id, verbose=False):
        """
        Initialize the object.

        plugin_id -- ID of this plugin
        verbose -- whether or not to enable verbose logging
        """
        self.adapters = {}
        self.notifiers = {}
        self.ipc_client = IpcClient(plugin_id, verbose=verbose)
        self.plugin_id = plugin_id
        self.verbose = verbose
        self.running = True
        self.thread = threading.Thread(target=self.recv)
        self.thread.daemon = True
        self.thread.start()

    def close(self):
        """Close the proxy."""
        self.running = False

        try:
            self.ipc_client.manager_socket.close()
            self.ipc_client.plugin_socket.close()
        except NNError:
            pass

    def send_error(self, message):
        """
        Send an error notification.

        message -- error message
        """
        self.send('pluginError', {'message': message})

    def add_adapter(self, adapter):
        """
        Send a notification that an adapter has been added.

        adapter -- the Adapter that was added
        """
        if self.verbose:
            print('AddonManagerProxy: add_adapter:', adapter.id)

        self.adapters[adapter.id] = adapter
        self.send('addAdapter', {
            'adapterId': adapter.id,
            'name': adapter.name,
            'packageName': adapter.package_name,
        })

    def add_notifier(self, notifier):
        """
        Send a notification that a notifier has been added.

        notifier -- the Notifier that was added
        """
        if self.verbose:
            print('AddonManagerProxy: add_notifier:', notifier.id)

        self.notifiers[notifier.id] = notifier
        self.send('addNotifier', {
            'notifierId': notifier.id,
            'name': notifier.name,
            'packageName': notifier.package_name,
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

    def handle_outlet_added(self, outlet):
        """
        Send a notification that a new outlet has been added.

        outlet -- the Outlet that was added
        """
        if self.verbose:
            print('AddonManagerProxy: handle_outlet_added:', outlet.id)

        outlet_dict = outlet.as_dict()
        outlet_dict['notifierId'] = outlet.notifier.id
        self.send('handleOutletAdded', outlet_dict)

    def handle_outlet_removed(self, outlet):
        """
        Send a notification that a managed outlet was removed.

        outlet -- the Outlet that was removed
        """
        if self.verbose:
            print('AddonManagerProxy: handle_outlet_removed:', outlet.id)

        self.send('handleOutletRemoved', {
            'notifierId': outlet.notifier.id,
            'id': outlet.id,
        })

    def send_pairing_prompt(self, adapter, prompt, url=None, device=None):
        """
        Send a prompt to the UI notifying the user to take some action.

        adapter -- The adapter sending the prompt
        prompt -- The prompt to send
        url -- URL to site with further explanation or troubleshooting info
        device -- Device the prompt is associated with
        """
        data = {
            'adapterId': adapter.id,
            'prompt': prompt,
        }

        if url is not None:
            data['url'] = url

        if device is not None:
            data['deviceId'] = device.id

        self.send('pairingPrompt', data)

    def send_unpairing_prompt(self, adapter, prompt, url=None, device=None):
        """
        Send a prompt to the UI notifying the user to take some action.

        adapter -- The adapter sending the prompt
        prompt -- The prompt to send
        url -- URL to site with further explanation or troubleshooting info
        device -- Device the prompt is associated with
        """
        data = {
            'adapterId': adapter.id,
            'prompt': prompt,
        }

        if url is not None:
            data['url'] = url

        if device is not None:
            data['deviceId'] = device.id

        self.send('unpairingPrompt', data)

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

    def send_action_status_notification(self, action):
        """
        Send a notification that an action's status changed.

        action -- the action whose status changed
        """
        self.send('actionStatus', {
            'adapterId': action.device.adapter.id,
            'deviceId': action.device.id,
            'action': action.as_dict(),
        })

    def send_event_notification(self, event):
        """
        Send a notification that an event occurred.

        event -- the event that occurred
        """
        self.send('event', {
            'adapterId': event.device.adapter.id,
            'deviceId': event.device.id,
            'event': event.as_dict(),
        })

    def send_connected_notification(self, device, connected):
        """
        Send a notification that a device's connectivity state changed.

        device -- the device object
        connected -- the new connectivity state
        """
        self.send('connected', {
            'adapterId': device.adapter.id,
            'deviceId': device.id,
            'connected': connected,
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

        try:
            self.ipc_client.plugin_socket.send(json.dumps({
                'messageType': msg_type,
                'data': data,
            }).encode('utf-8'))
        except NNError as e:
            print('AddonManagerProxy: Failed to send message: {}'.format(e))

    def recv(self):
        """Read a message from the IPC socket."""
        while self.running:
            try:
                msg = self.ipc_client.plugin_socket.recv()
            except NNError as e:
                print('AddonManagerProxy: Error receiving message from '
                      'socket: {}'.format(e))
                break

            if self.verbose:
                print('AddonMangerProxy: recv:', msg)

            if not msg:
                break

            try:
                msg = json.loads(msg.decode('utf-8'))
            except ValueError:
                print('AddonManagerProxy: Error parsing message as JSON')
                continue

            if 'messageType' not in msg:
                print('AddonManagerProxy: Invalid message')
                continue

            msg_type = msg['messageType']

            if msg_type == 'unloadPlugin':
                self.send('pluginUnloaded', {})

                def close_fn(proxy):
                    # Give the message above time to be sent and received.
                    time.sleep(.5)
                    proxy.close()

                self.make_thread(close_fn, args=(self,))
                break

            if 'data' not in msg:
                print('AddonManagerProxy: data not present in message')
                continue

            if 'notifierId' in msg['data']:
                notifier_id = msg['data']['notifierId']
                if notifier_id not in self.notifiers:
                    print('AddonManagerProxy: Unrecognized notifier, ignoring '
                          'message.')
                    continue

                notifier = self.notifiers[notifier_id]

                if msg_type == 'unloadNotifier':
                    def unload_fn(proxy, notifier):
                        notifier.unload()
                        proxy.send('notifierUnloaded',
                                   {'notifierId': notifier.id})

                    self.make_thread(unload_fn, args=(self, notifier))
                    del self.notifiers[notifier.id]
                    continue

                if msg_type == 'notify':
                    def notify_fn(proxy, notifier):
                        outlet_id = msg['data']['outletId']
                        outlet = notifier.get_outlet(outlet_id)
                        if outlet is None:
                            print('AddonManagerProxy: No such outlet, '
                                  'ignoring message.')
                            return

                        message_id = msg['data']['messageId']

                        try:
                            outlet.notify(msg['data']['title'],
                                          msg['data']['message'],
                                          msg['data']['level'])

                            proxy.send('notifyResolved', {
                                'messageId': message_id,
                            })
                        except NotifyError:
                            proxy.send('notifyRejected', {
                                'messageId': message_id,
                            })

                    self.make_thread(notify_fn, args=(self, notifier))
                    continue

                continue

            if 'adapterId' not in msg['data']:
                print('AddonManagerProxy: Adapter ID not present in message.')
                continue

            adapter_id = msg['data']['adapterId']
            if adapter_id not in self.adapters:
                print('AddonManagerProxy: Unrecognized adapter, ignoring '
                      'message.')
                continue

            adapter = self.adapters[adapter_id]

            # High-level adapter messages
            if msg_type == 'startPairing':
                self.make_thread(adapter.start_pairing,
                                 args=(msg['data']['timeout'],))
                continue

            if msg_type == 'cancelPairing':
                self.make_thread(adapter.cancel_pairing)
                continue

            if msg_type == 'unloadAdapter':
                def unload_fn(proxy, adapter):
                    adapter.unload()
                    proxy.send('adapterUnloaded',
                               {'adapterId': adapter.id})

                self.make_thread(unload_fn, args=(self, adapter))
                del self.adapters[adapter.id]
                continue

            # All messages from here on are assumed to require a valid deviceId
            if 'data' not in msg or 'deviceId' not in msg['data']:
                print('AddonManagerProxy: No deviceId present in message, '
                      'ignoring.')
                continue

            device_id = msg['data']['deviceId']
            if msg_type == 'removeThing':
                self.make_thread(adapter.remove_thing, args=(device_id,))
                continue

            if msg_type == 'cancelRemoveThing':
                self.make_thread(adapter.cancel_remove_thing,
                                 args=(device_id,))
                continue

            if msg_type == 'setProperty':
                def set_prop_fn(proxy, adapter):
                    dev = adapter.get_device(device_id)
                    if not dev:
                        return

                    prop = dev.find_property(msg['data']['propertyName'])
                    if not prop:
                        return

                    try:
                        prop.set_value(msg['data']['propertyValue'])
                        if prop.fire_and_forget:
                            proxy.send_property_changed_notification(prop)
                    except PropertyError:
                        proxy.send_property_changed_notification(prop)

                self.make_thread(set_prop_fn, args=(self, adapter))
                continue

            if msg_type == 'requestAction':
                def request_action_fn(proxy, adapter):
                    action_id = msg['data']['actionId']
                    action_name = msg['data']['actionName']

                    try:
                        dev = adapter.get_device(device_id)

                        if dev:
                            action_input = None
                            if 'input' in msg['data']:
                                action_input = msg['data']['input']

                            dev.request_action(action_id,
                                               action_name,
                                               action_input)

                        proxy.send('requestActionResolved', {
                            'actionName': action_name,
                            'actionId': action_id,
                        })
                    except ActionError:
                        proxy.send('requestActionRejected', {
                            'actionName': action_name,
                            'actionId': action_id,
                        })

                self.make_thread(request_action_fn, args=(self, adapter))
                continue

            if msg_type == 'removeAction':
                def remove_action_fn(proxy, adapter):
                    action_id = msg['data']['actionId']
                    action_name = msg['data']['actionName']
                    message_id = msg['data']['messageId']

                    try:
                        dev = adapter.get_device(device_id)

                        if dev:
                            dev.remove_action(action_id, action_name)

                        proxy.send('removeActionResolved', {
                            'actionName': action_name,
                            'actionId': action_id,
                            'messageId': message_id,
                        })
                    except ActionError:
                        proxy.send('removeActionRejected', {
                            'actionName': action_name,
                            'actionId': action_id,
                            'messageId': message_id,
                        })

                self.make_thread(remove_action_fn, args=(self, adapter))
                continue

            if msg_type == 'setPin':
                def set_pin_fn(proxy, adapter):
                    message_id = msg['data']['messageId']

                    try:
                        adapter.set_pin(device_id, msg['data']['pin'])

                        dev = adapter.get_device(device_id)
                        proxy.send('setPinResolved', {
                            'device': dev.as_dict(),
                            'messageId': message_id,
                            'adapterId': adapter.id,
                        })
                    except SetPinError:
                        proxy.send('setPinRejected', {
                            'deviceId': device_id,
                            'messageId': message_id,
                        })

                self.make_thread(set_pin_fn, args=(self, adapter))
                continue

            if msg_type == 'setCredentials':
                def set_credentials_fn(proxy, adapter):
                    message_id = msg['data']['messageId']

                    try:
                        adapter.set_credentials(device_id,
                                                msg['data']['username'],
                                                msg['data']['password'])

                        dev = adapter.get_device(device_id)
                        proxy.send('setCredentialsResolved', {
                            'device': dev.as_dict(),
                            'messageId': message_id,
                            'adapterId': adapter.id,
                        })
                    except SetCredentialsError:
                        proxy.send('setCredentialsRejected', {
                            'deviceId': device_id,
                            'messageId': message_id,
                        })

                self.make_thread(set_credentials_fn, args=(self, adapter))
                continue

    @staticmethod
    def make_thread(target, args=()):
        """
        Start up a thread in the background.

        target -- the target function
        args -- arguments to pass to target
        """
        t = threading.Thread(target=target, args=args)
        t.daemon = True
        t.start()
