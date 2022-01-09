import re

MAX_SUPPLY_RAW = "340282366920938463463374607431768211455"

# These are the official units of Nano cryptocurrency.
# "NANO" or "Nano" is the reference unit used currently by most speakers when they refer to Nano.
REPRESENTATIONS = {
    "GNano": 10**33,
    "NANO": 10**30,
    "knano": 10**27,
    "nyano": 10**24,
    "mnano": 10**21,
    "unano": 10**18,
    "raw": 1,
}


class Amount:
    AMOUNT_STRING_REGEX = r"([0-9.]+)([A-z ]+)"

    def __init__(self, raw_input, unit=None):
        """
        Amount representation of the input data.

        Usage examples:

            amount = Amount(1)  # 1 NANO
            amount = Amount(1.33)  # 1.33 Nano
            amount = Amount("1.33")  # 1.33 Nano
            amount = Amount("1.33", unit="nyano")  # 1330000 Nano
            amount = Amount("1.33 nyano")  # 1330000 Nano
            amount = Amount("1.33 NANO")  # 1.33 Nano

        Amounts can be operated with classical integer operations. For example, the following is possible:
            >>> a = Amount("4150000 nyano")
            >>> b = Amount("4.15 NANO")
            >>> b == a
            True

        :param raw_input:
            A string containing the values, a float number or an integer.
            If it is a string, it could have appended the unit representation at the right (with or without space)
            If no unit representation is provided as string, the one set in the parameter `unit` is taken.

            Note: a string representation is preferred.

        :param unit:
            Unit representation of the amount. If not set, "NANO" is set by default unless `raw_input` is a string and contains the unit.
            The following values are supported:
                "GNano"
                "NANO"
                "knano"
                "nyano"
                "mnano"
                "unano"
                "raw"

            This parameter overrides unit values in raw_input in case it is text and was provided.
        """
        self._value, self._representation_unit = self._decimal(raw_input, unit=unit)

    @property
    def unit(self):
        return self._representation_unit

    @staticmethod
    def _decimal(comma_string, unit=None):

        if type(comma_string) is Amount:
            unit = unit if unit is not None else comma_string.unit
            return comma_string._value, unit

        if type(comma_string) in [float, int]:
            comma_string = str(comma_string)

        if "-" in comma_string:
            raise ValueError("Negative amounts not supported.")

        # First we try to seek for the unit text (in case)
        match = re.match(Amount.AMOUNT_STRING_REGEX, comma_string, re.I)

        if match:
            comma_string, unit_detected = match.groups()
            comma_string = comma_string.strip()

            # We override the detected unit by the unit given as parameter
            unit = unit_detected.strip() if unit is None else unit
        else:
            unit = unit if unit is not None else "NANO"

        representation_unit_val = REPRESENTATIONS.get(unit, None)

        if representation_unit_val is None:
            raise ValueError(
                f"'{unit}' is not a valid representation unit. The allowed representations are: {list(REPRESENTATIONS)}")

        if "." not in comma_string:
            comma_string = comma_string + ".0"

        comma_string_split = comma_string.split(".")

        integer = comma_string_split[0]
        decimals = comma_string_split[1]

        # We transform the comma_string under the unit representation into RAW
        zeros_remaining_right = len(str(representation_unit_val)) - len(decimals) - 1
        raw_value = f'{integer}{decimals[:zeros_remaining_right]}{"0" * zeros_remaining_right}'

        zeros_remaining_left = len(MAX_SUPPLY_RAW) - len(raw_value)
        raw_value = f'{"0" * zeros_remaining_left}{raw_value}'

        if unit == "raw" and "." in raw_value:
            raw_value = raw_value.split(".")[0]

        return raw_value, unit

    @classmethod
    def from_value(cls, value, unit):
        instance = cls(0, unit=unit)
        instance._value = value
        return instance

    def as_unit(self, new_unit="NANO"):
        return Amount.from_value(self._value, unit=new_unit)

    def __str__(self):
        return str(int(self._value))

    def format(self, show_unit=True, squeeze_zeros=True):
        representation_unit_val = REPRESENTATIONS.get(self._representation_unit, None)

        if representation_unit_val is None:
            raise ValueError("Representation unit not valid. Amount object is bad constructed.")

        comma_position = len(MAX_SUPPLY_RAW) - (len(str(representation_unit_val)) - 1)

        if comma_position == 38:
            comma_position = 39

        integer = self._value[:comma_position]
        decimal = self._value[comma_position:]

        if squeeze_zeros:
            integer = str(int(integer))
            if decimal != "":
                decimal = str(int(decimal[::-1]))[::-1]

        result = f"{integer}"

        if decimal != "" and self._representation_unit != "raw":
            result += f".{decimal}"

        if show_unit:
            result = result + f" {self._representation_unit}"

        return result

    def __repr__(self):
        return self.format(show_unit=True, squeeze_zeros=True)

        # ARITHMETIC OPERATIONS

    def __add__(self, add_with):
        return Amount(int(self._value) + int(Amount(add_with)._value), unit="raw").as_unit(self._representation_unit)

    def __sub__(self, sub_with):
        return Amount(int(self._value) - int(Amount(sub_with)._value), unit="raw").as_unit(self._representation_unit)

    def __mul__(self, mul_with):
        return Amount(int(self._value) * mul_with, unit="raw").as_unit(self._representation_unit)

    def __floordiv__(self, div_with):
        return Amount(int(self._value) // div_with, unit="raw").as_unit(self._representation_unit)

    def __truediv__(self, div_with):
        return self.__floordiv__(div_with)

    def __mod__(self, other):
        return Amount(int(self._value) % other, unit="raw").as_unit(self._representation_unit)

    def __pow__(self, exponent):
        raise NotImplementedError("Pow operation not supported on amounts.")

    def __lt__(self, other):
        return int(self._value) < int(Amount(other)._value)

    def __le__(self, other):
        return int(self._value) <= int(Amount(other)._value)

    def __eq__(self, other):
        return int(self._value) == int(Amount(other)._value)

    def __ne__(self, other):
        return int(self._value) != int(Amount(other)._value)

    def __gt__(self, other):
        return int(self._value) > int(Amount(other)._value)

    def __ge__(self, other):
        return int(self._value) >= int(Amount(other)._value)

    def clone(self):
        return Amount(self)

    def __isub__(self, other):
        return self - other

    def __iadd__(self, other):
        return self + other

    def __imul__(self, other):
        return self * other

    def __idiv__(self, other):
        return self / other

    def __ifloordiv__(self, other):
        return self // other

    def __imod__(self, other):
        return self % other

    def __ipow__(self, other):
        return self ** other

    def __format__(self, *args, **kwargs):
        return self.format(*args, **kwargs)

    def to_hex(self, expected_bytes=None):
        if expected_bytes is None:
            expected_bytes = 0

        d = int(self._value)
        result = ""
        decimal_map = list("0123456789ABCDEF")

        while d > 0:
            result += decimal_map[int(d % 16)]
            d //= 16

        return result[::-1].zfill(expected_bytes * 2)
