class EventManager(object):
    def __init__(self, genv):
        self.events = {}
    
    def __getitem__(self, name):
        try:
            event = self.events[name]
        except KeyError:
            event = Event(name)
            self.events[name] = event
        return event

class Event(object):
    def __init__(self, name):
        self.name = name
        self.subscribers = set()
    
    def subscribe(self, callback):
        self.subscribers.add(callback)
    
    def unsubscribe(self, callback):
        self.subscribers.remove(callback)
    
    def send(self, *args, **kwargs):
        print "Sending event %s" % self.name
        for callback in self.subscribers:
            callback(*args, **kwargs)
