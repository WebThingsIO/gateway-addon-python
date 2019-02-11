"""Exception types."""


class ActionError(Exception):
    """Exception to indicate an issue with an action."""

    pass


class PropertyError(Exception):
    """Exception to indicate an issue with a property."""

    pass


class SetPinError(Exception):
    """Exception to indicate an issue with setting a PIN."""

    pass


class SetCredentialsError(Exception):
    """Exception to indicate an issue with setting the credentials."""

    pass
