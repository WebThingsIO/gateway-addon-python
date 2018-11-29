"""High-level Property base class implementation."""

from .errors import PropertyError


class Property:
    """A Property represents an individual state value of a device."""

    def __init__(self, device, name, description):
        """
        Initialize the object.

        device -- the Device this property belongs to
        name -- name of the property
        description -- description of the property, as a dictionary
        """
        self.device = device
        self.name = name
        self.value = None
        self.description = {}
        self.visible = True
        self.fire_and_forget = False

        if 'visible' in description:
            self.visible = description['visible']

        # Check 'min' and 'max' for backwards compatibility
        if 'min' in description:
            self.description['minimum'] = description['min']

        if 'max' in description:
            self.description['maximum'] = description['max']

        fields = [
            'label',
            'type',
            '@type',
            'unit',
            'description',
            'minimum',
            'maximum',
            'enum',
            'readOnly',
            'multipleOf',
            'links',
        ]
        for field in fields:
            if field in description:
                self.description[field] = description[field]

    def as_dict(self):
        """
        Get the property state as a dictionary.

        Returns the state as a dictionary.
        """
        prop = {
            'name': self.name,
            'value': self.value,
            'visible': self.visible,
        }
        prop.update(self.description)
        return prop

    def as_property_description(self):
        """
        Get the property description.

        Returns a dictionary describing the property.
        """
        return self.description

    def is_visible(self):
        """Return whether or not this property is visible."""
        return self.visible

    def set_cached_value(self, value):
        """
        Set the cached value of the property, making adjustments as necessary.

        value -- the value to set

        Returns the value that was set.
        """
        if 'type' in self.description and \
                self.description['type'] == 'boolean':
            self.value = bool(value)
        else:
            self.value = value

        return self.value

    def get_value(self):
        """
        Get the current property value.

        Returns the value.
        """
        return self.value

    def set_value(self, value):
        """
        Set the current value of the property.

        value -- the value to set
        """
        if 'readOnly' in self.description and self.description['readOnly']:
            raise PropertyError('Read-only property')

        if 'minimum' in self.description and \
                value < self.description['minimum']:
            raise PropertyError('Value less than minimum: {}'
                                .format(self.description['minimum']))

        if 'maximum' in self.description and \
                value > self.description['maximum']:
            raise PropertyError('Value greater than maximum: {}'
                                .format(self.description['maximum']))

        if 'multipleOf' in self.description and \
                value % self.description['multipleOf'] != 0:
            raise PropertyError('Value is not a multiple of: {}'
                                .format(self.description['multipleOf']))

        if 'enum' in self.description and \
                len(self.description['enum']) > 0 and \
                value not in self.description['enum']:
            raise PropertyError('Invalid enum value')

        self.set_cached_value(value)
        self.device.notify_property_changed(self)
