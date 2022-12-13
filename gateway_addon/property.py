"""High-level Property base class implementation."""

from .errors import PropertyError
import warnings


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

        # Check 'visible' for backwards compatibility
        if 'visible' in description:
            warnings.warn('''The visible member of property descriptions is
            deprecated.''', DeprecationWarning)
            self.visible = description['visible']

        # Check 'min' and 'max' for backwards compatibility
        if 'min' in description:
            self.description['minimum'] = description['min']

        if 'max' in description:
            self.description['maximum'] = description['max']

        # Check 'label' for backwards compatibility
        if 'label' in description:
            self.description['title'] = description['label']

        fields = [
            'title',
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

    def set_cached_value_and_notify(self, value):
        """
        Set the cached value of the property and notify the device if changed.

        value -- the value to set

        Returns True if the value has changed, False otherwise.
        """
        old_value = self.value
        self.set_cached_value(value)

        # set_cached_value may change the value, therefore we have to check
        # self.value after the call to set_cached_value
        has_changed = old_value != self.value

        if has_changed:
            self.device.notify_property_changed(self)

        return has_changed

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

        if 'multipleOf' in self.description:
            # note that we don't use the modulus operator here because it's
            # unreliable for floating point numbers
            multiple_of = self.description['multipleOf']
            if value / multiple_of - round(value / multiple_of) != 0:
                raise PropertyError('Value is not a multiple of: {}'
                                    .format(multiple_of))

        if 'enum' in self.description and \
                len(self.description['enum']) > 0 and \
                value not in self.description['enum']:
            raise PropertyError('Invalid enum value')

        self.set_cached_value_and_notify(value)
