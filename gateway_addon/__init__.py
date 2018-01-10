"""This module provides a high-level interface for creating Gateway add-ons."""
# flake8: noqa
from .adapter import Adapter
from .addon_manager_proxy import AddonManagerProxy
from .device import Device
from .ipc import IpcClient
from .property import Property

API_VERSION = 1
