"""IPC client to communicate with the Gateway."""

from __future__ import print_function
from nnpy.errors import NNError
import functools
import json
import jsonschema
import nnpy
import os

from .constants import MessageType


_IPC_BASE = 'ipc:///tmp/'
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

    def __init__(self, plugin_id, verbose=False):
        """
        Initialize the object.

        plugin_id -- ID of this plugin
        verbose -- whether or not to enable verbose logging
        """
        self.manager_socket = nnpy.Socket(nnpy.AF_SP, nnpy.REQ)
        self.manager_conn = \
            self.manager_socket.connect(_IPC_BASE + 'gateway.addonManager')

        with open(os.path.join(_SCHEMA_DIR, 'schema.json'), 'rt') as f:
            schema = json.load(f)

        self.validator = jsonschema.Draft7Validator(
            schema=schema,
            resolver=Resolver()
        )

        if verbose:
            print('IpcClient: Connected to server, registering...')

        try:
            self.manager_socket.send(json.dumps({
                'messageType': MessageType.PLUGIN_REGISTER_REQUEST,
                'data': {
                    'pluginId': plugin_id,
                }
            }).encode('utf-8'))
        except NNError as e:
            print('IpcClient: Failed to send message: {}'.format(e))
            return

        try:
            resp = self.manager_socket.recv()
        except NNError as e:
            print('IpcClient: Error receiving message: {}'.format(e))
            return

        if verbose:
            print('IpcClient: Received manager message: {}'.format(resp))

        try:
            resp = json.loads(resp.decode('utf-8'))

            self.validator.validate({'message': resp})

            if resp['messageType'] != MessageType.PLUGIN_REGISTER_RESPONSE:
                raise ValueError()

            self.plugin_socket = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
            self.plugin_conn = self.plugin_socket.connect(
                _IPC_BASE + resp['data']['ipcBaseAddr'])
            self.gateway_version = resp['data']['gatewayVersion']
            self.user_profile = resp['data']['userProfile']

            if verbose:
                print('IpcClient: Registered with PluginServer')
        except ValueError:
            print('IpcClient: Unexpected registration reply from gateway: {}'
                  .format(resp))
        except jsonschema.exceptions.ValidationError:
            print('Invalid message received:', resp)
