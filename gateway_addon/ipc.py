"""IPC client to communicate with the Gateway."""

from nnpy.errors import NNError
import json
import nnpy


_IPC_BASE = 'ipc:///tmp/'


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

        if verbose:
            print('IpcClient: Connected to server, registering...')

        try:
            self.manager_socket.send(json.dumps({
                'messageType': 'registerPlugin',
                'data': {
                    'pluginId': plugin_id,
                }
            }))
        except NNError as e:
            print('IpcClient: Failed to send message: {}'.format(e))
            return

        try:
            resp = self.manager_socket.recv()
        except NNError as e:
            print('IpcClient: Error receiving message: {}'.format(e))
            return

        if verbose:
            print('IpcClient: Received manager message:', resp)

        try:
            resp = json.loads(resp)
            if not resp or 'messageType' not in resp or \
                    resp['messageType'] != 'registerPluginReply':
                raise ValueError()

            self.plugin_socket = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
            self.plugin_conn = self.plugin_socket.connect(
                _IPC_BASE + resp['data']['ipcBaseAddr'])

            if verbose:
                print('IpcClient: Registered with PluginServer')
        except ValueError:
            print('IpcClient: Unexpected registration reply from gateway:',
                  resp)
