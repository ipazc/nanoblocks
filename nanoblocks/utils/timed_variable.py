import time

from nanoblocks.utils.time import now


class TimedVariable:
    """
    Represents a variable that also tracks its last update.

    Internally, a monotonic timer is used, meaning that it can not go backwards.
    This means that this class is protected against calendar time changes.

    Usage example:

    >>> import time
    >>> variable = TimedVariable("value")
    >>> print(variable.value)
    "value"
    >>> time.sleep(2)
    >>> print(variable.last_update_elapsed_time)
    2.0
    >>> variable.value = "new_value"
    >>> time.sleep(1)
    >>> print(variable.last_update_elapsed_time)
    1.0
    """
    def __init__(self, variable):
        self._monotonic_timestamp = None
        self._value = None
        self.value = variable

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self._monotonic_timestamp = time.monotonic()

    @property
    def last_update_elapsed_time(self):
        return time.monotonic() - self._monotonic_timestamp

    def refresh(self):
        self._monotonic_timestamp = time.monotonic()

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        return str(self._value)

    def _repr_html_(self):
        if hasattr(self._value, "_repr_html_"):
            # noinspection PyProtectedMember
            return self._value._repr_html_()
        else:
            return repr(self)
