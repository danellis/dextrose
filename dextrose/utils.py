import sys
from time import time

def titlize(s):
    return ''.join(map(lambda s: s.title(), s.split('_')))

def interpret_file(filename, locals=None):
    """Execute a file that isn't necessarily in the Python path."""

    with file(filename, 'r') as f:
        code = compile(f.read(), filename, 'exec')
        eval(code, globals(), locals or {})

class Metaclass(type):
    """A metaclass that runs class mutators that are registered by calling them within a class
    definition."""
    
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        if cls.is_subclass():
            cls.init_subclass(name, bases, attrs)
        if hasattr(cls, '_dx_class_mutators'):
            for mutator in cls._dx_class_mutators:
                mutator(cls)
    
    def is_subclass(cls):
        return reduce(
            lambda x, y: x or y,
            [isinstance(b, cls.__class__) for b in cls.__bases__]
        )
        
    def init_subclass(cls, name, bases, attrs):
        pass

class ClassMutator(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        attrs = sys._getframe(1).f_locals
        mutators = attrs.setdefault('_dx_class_mutators', [])
        mutators.append(self)

    def __call__(self, cls):
        self.mutate(cls, *self.args, **self.kwargs)
        
    @staticmethod
    def run_mutators(cls):
        if hasattr(cls, '_dx_class_mutators'):
            for mutator in cls._dx_class_mutators:
                mutator(cls)

class ModuleNotFound(ImportError):
    """
    No module was found because none exists.
    """
            
def import_module(*args):
    """Taken from twisted.python.reflect.
    
    Import the given name as a module, then walk the stack to determine whether
    the failure was the module not existing, or some code in the module (for
    example a dependent import) failing.  This can be helpful to determine
    whether any actual application code was run.  For example, to distiguish
    administrative error (entering the wrong module name), from programmer
    error (writing buggy code in a module that fails to import).

    @raise Exception: if something bad happens.  This can be any type of
    exception, since nobody knows what loading some arbitrary code might do.

    @raise ModuleNotFound: if no module was found.
    """
    import_name = '.'.join(args)
    try:
        try:
            return __import__(import_name, None, None, [''])
        except ImportError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            while exc_traceback:
                exc_name = exc_traceback.tb_frame.f_globals["__name__"]
                if (exc_name is None or # python 2.4+, post-cleanup
                    exc_name == import_name): # python 2.3, no cleanup
                    raise exc_type, exc_value, exc_traceback
                exc_traceback = exc_traceback.tb_next
            raise ModuleNotFound()
    except:
        # Necessary for cleaning up modules in 2.3.
        sys.modules.pop(import_name, None)
        raise

class ExecutionTimer(object):
    def __init__(self, text):
        self.text = text
    
    def __enter__(self):
        self.start = time()
    
    def __exit__(self, type, value, traceback):
        print "%s: %s seconds" % (self.text, time() - self.start)
