"""High-level Device base class implementation."""

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .action import Action


class Device:
    """A Device represents a physical object being managed by an Adapter."""

    def __init__(self, adapter, _id):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- the device's individual ID
        """
        self.adapter = adapter
        self.id = str(_id)
        self.type = 'thing'
        self._context = 'https://iot.mozilla.org/schemas'
        self._type = []
        self.name = ''
        self.description = ''
        self.properties = {}
        self.actions = {}
        self.events = {}
        self.base_href = None
        self.pin_required = False
        self.pin_pattern = None
        self.credentials_required = False

    def as_dict(self):
        """
        Get the device state as a dictionary.

        Returns the state as a dictionary.
        """
        properties = {k: v.as_dict() for k, v in self.properties.items()}
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            '@context': self._context,
            '@type': self._type,
            'description': self.description,
            'properties': properties,
            'actions': self.actions,
            'events': self.events,
            'baseHref': self.base_href,
            'pin': {
                'required': self.pin_required,
                'pattern': self.pin_pattern,
            },
            'credentialsRequired': self.credentials_required,
        }

    def as_thing(self):
        """
        Return the device state as a Thing Description.

        Returns the state as a dictionary.
        """
        thing = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            '@context': self._context,
            '@type': self._type,
            'properties': self.get_property_descriptions(),
            'baseHref': self.base_href,
            'pin': {
                'required': self.pin_required,
                'pattern': self.pin_regex,
            },
            'credentialsRequired': self.credentials_required,
        }

        if self.description:
            thing['description'] = self.description

        return thing

    def get_id(self):
        """
        Get the ID of the device.

        Returns the ID as a string.
        """
        return self.id

    def get_name(self):
        """
        Get the name of the device.

        Returns the name as a string.
        """
        return self.name

    def get_type(self):
        """
        Get the type of the device.

        Returns the type as a string.
        """
        return self.type

    def get_property_descriptions(self):
        """
        Get the device's properties as a dictionary.

        Returns the properties as a dictionary, i.e. name -> description.
        """
        return {k: v.as_property_description()
                for k, v in self.properties.items()}

    def find_property(self, property_name):
        """
        Find a property by name.

        property_name -- the property to find

        Returns a Property object, if found, else None.
        """
        return self.properties.get(property_name, None)

    def get_property(self, property_name):
        """
        Get a property's value.

        property_name -- the property to get the value of

        Returns the properties value, if found, else None.
        """
        prop = self.find_property(property_name)
        if prop:
            return prop.get_value()

        return None

    def has_property(self, property_name):
        """
        Determine whether or not this device has a given property.

        property_name -- the property to look for

        Returns a boolean, indicating whether or not the device has the
        property.
        """
        return property_name in self.properties

    def notify_property_changed(self, prop):
        """
        Notify the AddonManager in the Gateway that a device property changed.

        prop -- the property that changed
        """
        self.adapter.manager_proxy.send_property_changed_notification(prop)

    def action_notify(self, action):
        """
        Notify the AddonManager in the Gateway that an action's status changed.

        action -- the action whose status changed
        """
        self.adapter.manager_proxy.send_action_status_notification(action)

    def event_notify(self, event):
        """
        Notify the AddonManager in the Gateway that an event occurred.

        event -- the event that occurred
        """
        self.adapter.manager_proxy.send_event_notification(event)

    def connected_notify(self, connected):
        """
        Notify the AddonManager in the Gateway of the device's connectivity.

        connected -- whether or not the device is connected
        """
        self.adapter.manager_proxy.send_connected_notification(self, connected)

    def set_property(self, property_name, value):
        """
        Set a property value.

        property_name -- name of the property to set
        value -- value to set
        """
        prop = self.find_property(property_name)
        if not prop:
            return

        prop.set_value(value)

    def request_action(self, action_id, action_name, action_input):
        """
        Request that a new action be performed.

        action_id -- ID of the new action
        action_name -- name of the action
        action_input -- any inputs to the action
        """
        if action_name not in self.actions:
            return

        # Validate action input, if present.
        metadata = self.actions[action_name]
        if 'input' in metadata:
            try:
                validate(action_input, metadata['input'])
            except ValidationError:
                return

        action = Action(action_id, self, action_name, action_input)
        self.perform_action(action)

    def remove_action(self, action_id, action_name):
        """
        Remove an existing action.

        action_id -- ID of the action
        action_name -- name of the action
        """
        if action_name not in self.actions:
            return

        self.cancel_action(action_id, action_name)

    def perform_action(self, action):
        """
        Do anything necessary to perform the given action.

        action -- the action to perform
        """
        pass

    def cancel_action(self, action_id, action_name):
        """
        Do anything necessary to cancel the given action.

        action_id -- ID of the action
        action_name -- name of the action
        """
        pass

    def add_action(self, name, metadata):
        """
        Add an action.

        name -- name of the action
        metadata -- action metadata, i.e. type, description, etc., as a dict
        """
        if not metadata:
            metadata = {}

        if 'href' in metadata:
            del metadata['href']

        self.actions[name] = metadata

    def add_event(self, name, metadata):
        """
        Add an event.

        name -- name of the event
        metadata -- event metadata, i.e. type, description, etc., as a dict
        """
        if not metadata:
            metadata = {}

        if 'href' in metadata:
            del metadata['href']

        self.events[name] = metadata
