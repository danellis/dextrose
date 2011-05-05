class ComponentManager(object):
    def __init__(self):
        self.factories = {}
    
    def register_component(self, cls, name=None):
        if name is None:
            name = '%s.%s' % (cls.__module__, cls.__name__)
        factory = lambda args, kwargs: cls(*args, **kwargs)
        self.register_factory(factory, name)
    
    def register_singleton(self, instance, name=None):
        self.register_factory(lambda: instance, name)

    def register_factory(self, factory, name):
        self.factories[name] = factory
    
    def get_component(self, class_name, args, kwargs):
        factory = self.factories.get(class_name, None)
        if factory is None:
            raise RuntimeError("Required component '%s' has not been registered.")
        return factory(*args, **kwargs)

manager = ComponentManager()
register_component = manager.register_component
register_singleton = manager.register_singleton
register_factory = manager.register_factory

class Dependency(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        attribute_name = '_dx_component_%x' % id(self)
        component_instance = getattr(instance, attribute_name, None)
        if component_instance is not None:
            return component_instance
        
        global manager
        component_instance = manager.get_component(self.name, self.args, self.kwargs)
        setattr(instance, attribute_name, component_instance)
        return component_instance
