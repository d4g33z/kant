from copy import deepcopy
from inflection import underscore
from kant.eventstore.stream import EventStream
from kant.datamapper.base import ModelMeta, FieldMapping
from kant.datamapper.fields import *  # NOQA
from .exceptions import CommandError


class Aggregate(FieldMapping, metaclass=ModelMeta):
    def __init__(self):
        super().__init__()
        self._all_events = EventStream()
        self._events = EventStream()
        self._stored_events = EventStream()

    def all_events(self):
        return self._all_events

    def stored_events(self):
        return self._stored_events

    def get_events(self):
        return self._events

    def notify_save(self, new_version):
        self._events.clear()
        self._events.initial_version = new_version

    def fetch_events(self, events: EventStream):
        self._stored_events = deepcopy(events)
        self._all_events = deepcopy(self._stored_events)
        for event in events:
            self.dispatch(event, flush=False)

    def apply(self, event):
        event_name = underscore(event.__class__.__name__)
        method_name = 'apply_{0}'.format(event_name)
        try:
            method = getattr(self, method_name)
            method(event)
        except AttributeError:
            msg = "The command for '{}' is not defined".format(event.__class__.__name__)
            raise CommandError(msg)

    def dispatch(self, events, flush=True):
        if isinstance(events, list):
            received_events = list(events)
        else:
            received_events = [events]
        for event in received_events:
            self.apply(event)
            if flush:
                self._events.add(event)
                self._all_events.add(event)

    @property
    def current_version(self):
        return self._all_events.current_version

    @property
    def version(self):
        return self._all_events.initial_version

    @classmethod
    def from_stream(cls, stream):
        self = cls()
        self.fetch_events(stream)
        return self