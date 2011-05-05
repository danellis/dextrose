import os.path
from jinja2 import Environment, BaseLoader, ChoiceLoader, PackageLoader, FileSystemLoader
from dextrose.component import register_singleton

__all__ = ['Template']

class JinjaExtension(object):
    def __init__(self, app, config):
        environment = Environment(loader=Loader(os.path.join(app.directory, 'templates')))
        try:
            import markdown
            environment.filters['markdown'] = markdown.markdown
        except ImportError:
            pass
        component = JinjaComponent(environment)
        register_singleton(component, 'jinja')

class JinjaComponent(object):
    def __init__(self, environment):
        self.environment = environment
    
    def get(self, name):
        return self.environment.get_template(name)

class Loader(BaseLoader):
    def __init__(self, directory):
        self.directory = directory
    
    def get_source(self, environment, filename):
        if ':' in filename:
            package, filename = filename.split(':', 1)
            loader = ChoiceLoader([
                FileSystemLoader(os.path.join(self.directory, 'packages', package)),
                PackageLoader(package, '')
            ])
        else:
            loader = FileSystemLoader(self.directory)
        return loader.get_source(environment, filename)
