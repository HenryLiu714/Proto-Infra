from Events import *


class EventSink(object):
    def publish(self, event: Event):
        pass

class Context(object):
    def __init__(self, event_sink: EventSink):
        self.event_sink = event_sink

