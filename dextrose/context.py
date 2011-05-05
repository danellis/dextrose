from werkzeug import Local, LocalManager

class Context(object):
    locals = Local()
    local_manager = LocalManager([locals])
    current_context = locals('context')
    
    def __init__(self, app, environ=None, request=None, args=None):
        self.app = app
        self.environ = environ
        self.request = request
        self.args = args
        self.response = None

    def __enter__(self):
        self.locals.context = self
        for fn in self.app.get_hook_functions('context-start'):
            fn(self)
        return self
    
    def __exit__(self, type, value, traceback):
        for fn in self.app.get_hook_functions('context-end'):
            fn(self)
        del self.locals.context
