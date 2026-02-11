from datetime import datetime, timezone

from src.Events import *


class EventSink(object):
    def publish(self, event: Event):
        pass

class Context(object):
    def __init__(self, event_sink: EventSink):
        self.event_sink = event_sink

    def current_time(self) -> datetime:
        """
        Returns the current UTC time.
        Using timezone-aware objects prevents many common bugs.
        """
        return datetime.now(timezone.utc)
