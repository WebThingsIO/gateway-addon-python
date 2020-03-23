"""This module provides a high-level interface for creating Gateway add-ons."""

# flake8: noqa
from .action import Action
from .adapter import Adapter
from .addon_manager_proxy import AddonManagerProxy
from .api_handler import APIHandler
from .api_handler_utils import APIRequest, APIResponse
from .database import Database
from .device import Device
from .errors import (ActionError, APIHandlerError, NotifyError, PropertyError,
                     SetPinError, SetCredentialsError)
from .event import Event
from .ipc import IpcClient
from .notifier import Notifier
from .outlet import Outlet
from .property import Property

__version__ = '0.12.0'
API_VERSION = 2


def get_version():
    """Get the version of this package."""
    return __version__
