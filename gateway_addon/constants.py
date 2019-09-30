"""WebThings Gateway Constants."""

import glob
import json
import os


class MessageType:
    """Enumeration of IPC message types."""

    pass


# Build up message types dynamically from schemas
for fname in glob.glob(os.path.realpath(
        os.path.join(os.path.dirname(__file__), 'schema', 'messages', '*.json')
        )):
    with open(fname, 'rt') as f:
        schema = json.load(f)

    if 'properties' not in schema or 'messageType' not in schema['properties']:
        continue

    name = fname.split('/')[-1].split('.')[0].upper().replace('-', '_')
    value = schema['properties']['messageType']['const']

    setattr(MessageType, name, value)


class NotificationLevel:
    """Enumeration of notification levels."""

    LOW = 0
    NORMAL = 1
    HIGH = 2


DONT_RESTART_EXIT_CODE = 100
