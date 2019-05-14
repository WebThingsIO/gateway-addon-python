"""This module provides a high-level interface for creating Gateway add-ons."""

# flake8: noqa
from .action import Action
from .adapter import Adapter
from .addon_manager_proxy import AddonManagerProxy
from .database import Database
from .device import Device
from .errors import (ActionError, NotifyError, PropertyError,
                     SetPinError, SetCredentialsError)
from .event import Event
from .ipc import IpcClient
from .notifier import Notifier
from .outlet import Outlet
from .property import Property

API_VERSION = 2
