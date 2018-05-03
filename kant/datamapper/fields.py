"""
Test
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from cuid import cuid
from dateutil import parser as dateutil_parser


class Field(ABC):
    """
    **Field** is an abastract class that represents a serializable field into the event store.
    """

    def __init__(
        self, default=None, json_column=None, primary_key=False, *args, **kwargs
    ):
        self.primary_key = primary_key
        self.default = default
        self.json_column = json_column

    @abstractmethod
    def encode(self, value):
        return value

    @abstractmethod
    def parse(self, value):
        return value

    def default_value(self):
        if callable(self.default):
            return self.default()
        return self.default


class CUIDField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.primary_key:
            self.default = cuid

    def encode(self, value):
        return str(value)

    def parse(self, value):
        return value


class DecimalField(Field):

    def encode(self, value):
        return float(value)

    def parse(self, value):
        return Decimal(value)


class IntegerField(Field):

    def encode(self, value):
        return int(value)

    def parse(self, value):
        return int(value)


class DateTimeField(Field):

    def __init__(self, auto_now=False, *args, **kwargs):
        self.auto_now = auto_now
        super().__init__(*args, **kwargs)
        if self.auto_now:
            self.default = lambda: datetime.now()

    def encode(self, value):
        """
        >>> field = DateTimeField()
        >>> create_at = datetime(2009, 5, 28, 16, 15)
        >>> field.encode(create_at)
        '2009-05-28T16:15:00'
        """
        return value.isoformat()

    def parse(self, value):
        """
        >>> field = DateTimeField()
        >>> field.parse('2009-05-28T16:15:00')
        datetime.datetime(2009, 5, 28, 16, 15)
        >>> create_at = datetime(2009, 5, 28, 16, 15)
        >>> field.parse(create_at)
        datetime.datetime(2009, 5, 28, 16, 15)
        """
        if isinstance(value, str):
            return dateutil_parser.parse(value)
        if not isinstance(value, datetime):
            raise TypeError("expected string or datetime object")
        return value


class CharField(Field):

    def encode(self, value):
        """
        >>> field = CharField()
        >>> field.encode(123)
        '123'
        """
        return str(value)

    def parse(self, value):
        """
        >>> field = CharField()
        >>> field.parse(123)
        '123'
        """
        return str(value)


class BooleanField(Field):

    def encode(self, value):
        """
        >>> field = BooleanField()
        >>> field.encode(True)
        'true'
        >>> field.encode(False)
        'false'
        """
        if value:
            return "true"
        return "false"

    def parse(self, value):
        """
        >>> field = BooleanField()
        >>> field.parse(True)
        True
        >>> field.parse(False)
        False
        >>> field.parse('true')
        True
        >>> field.parse('false')
        False
        """
        if isinstance(value, str) and value.strip() == "false":
            return False
        return bool(value)
