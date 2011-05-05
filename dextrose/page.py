from werkzeug import redirect as redirect_response
from werkzeug.routing import MethodNotAllowed
from dextrose.http import Response
from dextrose.utils import ExecutionTimer
from dextrose.component import Dependency
from recollectives.version import version

class PageMetaclass(type):
    def __init__(self, name, bases, attrs):
        # Merge in styles and scripts from base classes
        scripts = attrs.get('scripts', [])
        stylesheets = attrs.get('stylesheets', [])
        for base in bases:
            scripts.extend(getattr(base, 'scripts', []))
            stylesheets.extend(getattr(base, 'stylesheets', []))
        self.scripts = scripts
        self.stylesheets = stylesheets

class Page(object):
    __metaclass__ = PageMetaclass

    scripts = []
    stylesheets = []
    
    templates = Dependency('jinja')
    
    def __init__(self, context):
        self.context = context
        self.app = context.app
        self.request = context.request
        self.args = context.args
        self.vars = {}
    
    def generate(self):
        verb = self.request.method.lower()
        if verb == 'post':
            field_name = getattr(self,  'post_type_field', 'post_type')
            post_type = self.request.form.get(field_name, None)
            if post_type:
                method = getattr(self, 'post_%s' % post_type, None)
                if method:
                    response = method()
                    return response
        method = getattr(self, verb, None)
        if method is None:
            raise MethodNotAllowed
        else:
            with ExecutionTimer("Page method"):
                response = method(**self.args)
            return response
    
    def __getitem__(self, key):
        return self.vars[key]
    
    def __setitem__(self, key, value):
        self.vars[key] = value
    
    def render(self, template_name, mimetype='text/html'):
        template = self.templates.get(template_name)
        vars = {
            'context': self.context,
            'request': self.request,
            'csrf_token': self.context.session.create_csrf_token(),
            '_dx_scripts': self.scripts,
            '_dx_stylesheets': self.stylesheets,
            'version': version
        }
        vars.update(self.vars)
        # vars.update(dict(
        #     (name, cls(self.app, self.api, self.context, name).render())
        #     for name, cls in self._widgets.items()
        # ))
        return Response(
            template.render(vars),
            mimetype=mimetype
        )
    
    def redirect(self, location, status=302):
        return redirect_response(location, status)

class context_attribute(object):
    def __init__(self, name):
        self.name = name
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            if hasattr(instance.context, self.name):
                return getattr(instance.context, self.name)
            raise AttributeError("%r doesn't have attribute context.%s" % (instance, self.name))
