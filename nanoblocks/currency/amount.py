import decimal
import math
from decimal import Decimal


# These are the official units of Nano cryptocurrency.
# "NANO" or "Nano" is the reference unit used currently by most speakers when they refer to Nano.

REPRESENTATION_Gnano = Decimal(10) ** Decimal(33)
REPRESENTATION_NANO = Decimal(10) ** Decimal(30)
REPRESENTATION_knano = Decimal(10) ** Decimal(27)
REPRESENTATION_nano = Decimal(10) ** Decimal(24)
REPRESENTATION_mnano = Decimal(10) ** Decimal(21)
REPRESENTATION_unano = Decimal(10) ** Decimal(18)
REPRESENTATION_raw = Decimal(1)

REPRESENTATION_LABEL = {
    REPRESENTATION_Gnano: "Gnano",    
    REPRESENTATION_NANO: "NANO",  # 1 NANO = 1.000.000 nanoblocks
    REPRESENTATION_knano: "knano",    
    REPRESENTATION_nano: "nanoblocks",
    REPRESENTATION_mnano: "mnano",
    REPRESENTATION_unano: "unano",
    REPRESENTATION_raw: "raw",
}


context = decimal.getcontext()
context.prec = 100


class Amount:
    """
    Represents a fixed amount of the cryptocurrency, based on the official units of the coin.
    In Python it is not possible to express values as big as 1 NANO (in raw units) inside a pure Integer.
    For this reason, this class handles integer by using the "Decimal" class.

    This class implements the Integer interface so it can be naturally used as an Integer.
    
    Example:
    
        >>> amount = Amount("342")  # 342 raw
        >>> amount = Amount.from_knano("342")  # 342 knano
        >>> amount = Amount.from_NANO("342")  # 342 NANO
        ...
        
    It allows arithmetic operations as if it was an Integer:
    
        >>> amount = amount * 2
        >>> amount
        684 NANO
    """
    def __init__(self, raw_string, representation=REPRESENTATION_NANO):
        if type(raw_string) is Amount:
            self._value = raw_string._value
        else:
            self._value = Decimal(raw_string)
        self._representation = representation
    
    @classmethod
    def from_NANO(cls, nano_string, representation=REPRESENTATION_NANO):
        new_amount = cls(Amount(Decimal(nano_string)*REPRESENTATION_NANO))
        return new_amount
    
    def as_Gnano(self):
        return Amount(self._value, representation=REPRESENTATION_Gnano)

    def as_NANO(self):
        return Amount(self._value, representation=REPRESENTATION_NANO)

    def as_knano(self):
        return Amount(self._value, representation=REPRESENTATION_knano)
    
    def as_nano(self):
        return Amount(self._value, representation=REPRESENTATION_nano)

    def as_mnano(self):
        return Amount(self._value, representation=REPRESENTATION_mnano)

    def as_unano(self):
        return Amount(self._value, representation=REPRESENTATION_unano)

    def as_raw(self):
        return Amount(self._value, representation=REPRESENTATION_raw)

    def as_custom(self, representation):
        return Amount(self._value, representation=representation)

    def to_hex(self, expected_bytes=None):
        if expected_bytes is None:
            expected_bytes = 0

        d = self.as_raw()._value
        result = ""
        decimal_map = list("0123456789ABCDEF")

        while d > 0:
            result += decimal_map[int(d % 16)]
            d //= 16
        return result[::-1].zfill(expected_bytes * 2)

    def __add__(self, add_with):
        return self.clone(self._value + Amount(add_with)._value)
    
    def __sub__(self, sub_with):
        return self.clone(self._value - Amount(sub_with)._value)
    
    def __mul__(self, mul_with):
        return self.clone(self._value * Amount(mul_with)._value)
    
    def __floordiv__(self, div_with):
        return self.clone(self._value // Amount(div_with)._value)

    def __truediv__(self, div_with):
        return self.clone(self._value / Amount(div_with)._value)
    
    def simple_str(self):
        commas_count = int(math.log10(self._representation))
        format_str = "{0:." + str(commas_count) + "f}"
        return format_str.format((self._value / self._representation)).strip()

    def int_str(self):
        return self.simple_str().split(".")[0].split(" ")[0]

    def __str__(self):
        return f'{self.simple_str()} {REPRESENTATION_LABEL[self._representation]}'
        
    def __lt__(self, other): 
        return self._value < Amount(other)._value

    def __le__(self, other): 
        return self._value <= Amount(other)._value
    
    def __eq__(self, other): 
        return self._value == Amount(other)._value

    def __ne__(self, other): 
        return self._value != Amount(other)._value

    def __gt__(self, other): 
        return self._value > Amount(other)._value

    def __ge__(self, other): 
        return self._value >= other._value

    def __mod__(self, other): 
        return self.clone(self._value % Amount(other)._value)

    def clone(self, override_value=None):
        return Amount(override_value if override_value is not None else self._value, representation=self._representation)
    
    def __pow__(self, other):
        return self.clone(self._value ** Amount(other)._value)
    
    def __repr__(self):
        return str(self)
    
    def __neg__(self):
        return self * -1
    
    def __pos__(self):
        return self * +1
        
    def __invert__(self):
        return self * -1
    
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
        return self.simple_str()
