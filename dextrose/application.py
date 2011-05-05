import os.path
import yaml
from werkzeug import import_string
from werkzeug.serving import run_simple
from dextrose.http import Response
from dextrose.context import Context
from dextrose.events import EventManager
from dextrose.dispatcher import Dispatcher
from dextrose.utils import import_module, titlize

def load_config(package, environment):
    """Load configuration from <package_dir>/config/<environment>.yaml"""
    filename = os.path.join(os.path.dirname(package.__file__), 'config', '%s.yaml' % environment)
    config_file = file(filename, 'r')
    config = yaml.load(config_file)
    return config

def load_application(package_name, environment):
    """Import and instantiate the application object. By default, this is dextrose.application.Application,
    but it can be specified as the 'class' option in the configuration file."""
    module = import_module(package_name)
    config = load_config(module, environment)
    app_class_name = config.get('class', 'dextrose.application.Application')
    app_class = import_string(app_class_name)
    app = app_class(module, config)
    return app

class Application(object):
    def __init__(self, module, config):
        self.module = module
        self.module_name = module.__name__
        self.directory = os.path.dirname(self.module.__file__)
        self.config = config
        self.hooks = {}
        self.events = EventManager(self)
        self.dispatcher = Dispatcher(self)
        self.load_extensions()

    def wsgi(self, environ, start_response):
        """WSGI entry point, delegated to ``Dispatcher.dispatch``."""
        response = self.dispatcher.dispatch(environ)
        return response(environ, start_response)

    def open_file(self, filename, mode='r'):
        # FIXME: Use pkg_resources
        full_filename = os.path.join(self.directory, filename)
        f = open(full_filename, mode)
        return f
    
    def load_extensions(self):
        self.extensions = {}
        for extension_name, extension_config in self.config['extensions'].items():
            print "Loading extension %s" % extension_name
            module = import_module(extension_name)
            class_name = '%sExtension' % titlize(extension_name.rsplit('.', 1)[-1])
            extension_class = getattr(module, class_name, None)
            if extension_class is None:
                raise RuntimeError("Extension %s is missing a %s class" % (extension_name, class_name))
            extension = extension_class(self, extension_config)
            self.extensions[extension_name] = extension

    def register_hook_function(self, name, function):
        hooks = self.hooks.setdefault(name, [])
        hooks.append(function)

    def get_hook_functions(self, name):
        functions = self.hooks.get(name, [])
        return functions
