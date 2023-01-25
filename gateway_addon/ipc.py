"""IPC client to communicate with the Gateway."""

from __future__ import print_function
import functools
import json
import jsonschema
import os
import threading
import time
import websocket

from .constants import MessageType


_IPC_PORT = 9500
_SCHEMA_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), 'schema')
)

print = functools.partial(print, flush=True)


class Resolver(jsonschema.RefResolver):
    """Resolver for $ref members in schemas."""

    def __init__(self):
        """Initialize the resolver."""
        jsonschema.RefResolver.__init__(
            self,
            base_uri='',
            referrer=None,
            cache_remote=True,
        )

    def resolve_remote(self, uri):
        """
        Resolve a remote URI. We only look locally.

        uri -- the URI to resolve
        """
        name = uri.split('/')[-1]
        local = os.path.join(_SCHEMA_DIR, 'messages', name)

        if os.path.exists(local):
            with open(local, 'rt') as f:
                return json.load(f)
        else:
            print('Unable to find referenced schema:', name)


class IpcClient:
    """IPC client which can communicate between the Gateway and an add-on."""

    def __init__(self, plugin_id, on_message, verbose=False):
        """
        Initialize the object.

        plugin_id -- ID of this plugin
        on_message -- message handler
        verbose -- whether or not to enable verbose logging
        """
        with open(os.path.join(_SCHEMA_DIR, 'schema.json'), 'rt') as f:
            schema = json.load(f)

        self.plugin_id = plugin_id
        self.verbose = verbose
        self.owner_message_handler = on_message

        self.validator = jsonschema.Draft7Validator(
            schema=schema,
            resolver=Resolver()
        )

        self.registered = False

        self.ws = websocket.WebSocketApp(
            'ws://127.0.0.1:{}/'.format(_IPC_PORT),
            on_open=self.on_open,
            on_message=self.on_message,
        )

        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()

        while not self.registered:
            time.sleep(0.01)

    def on_open(self, _):
        """Event handler for WebSocket opening."""
        if self.verbose:
            print('IpcClient: Connected to server, registering...')

        try:
            self.ws.send(json.dumps({
                'messageType': MessageType.PLUGIN_REGISTER_REQUEST,
                'data': {
                    'pluginId': self.plugin_id,
                }
            }))
        except websocket.WebSocketException as e:
            print('IpcClient: Failed to send message: {}'.format(e))
            return

    def on_message(self, _, message):
        """
        Event handler for WebSocket messages.

        message -- the received message
        """
        try:
            resp = json.loads(message)

            self.validator.validate({'message': resp})

            if resp['messageType'] == MessageType.PLUGIN_REGISTER_RESPONSE:
                if self.verbose:
                    print('IpcClient: Registered with PluginServer')

                self.gateway_version = resp['data']['gatewayVersion']
                self.user_profile = resp['data']['userProfile']
                self.preferences = resp['data']['preferences']
                self.registered = True
            else:
                self.owner_message_handler(resp)
        except ValueError:
            print('IpcClient: Unexpected registration reply from gateway: {}'
                  .format(resp))
        except jsonschema.exceptions.ValidationError:
            print('Invalid message received:', resp)

    def close(self):
        """Close the WebSocket."""
        self.ws.close()
