import sys, os.path, re
import json
from werkzeug import routing, import_string, redirect, extract_path_info
from werkzeug.routing import Map, Rule, BaseConverter, NotFound
from werkzeug.exceptions import HTTPException, NotFound
from dextrose.context import Context
from dextrose.http import Request, Response, JsonResponse
from dextrose import ConfigurationError

# Allow variable names in rules to begin with an underscore
routing._rule_re = re.compile(r'''
    (?P<static>[^<]*)                           # static rule data
    <
    (?:
        (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
        (?:\((?P<args>.*?)\))?                  # converter arguments
        \:                                      # variable delimiter
    )?
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)         # variable name
    >
''', re.VERBOSE)

class Dispatcher(object):
    """Dispatch requests based on a WSGI environment.
        
    The routes are loaded from the <package>/config/routes file, and each line should be blank,
    a comment, or one of the following:
        <route> <page class>
        <route> redirect:<url>
        <route> template:<filename>
    """
    
    def __init__(self, app):
        """Load the URL routing map and instantiate the responders."""
 
        self.app = app
        
        # Set up URL routing
        self.map = Map()
        routes_file = file(os.path.join(app.directory, 'config', 'routes'), 'r')
        for line in routes_file:
            # Split the line from one of the documented formats
            parts = line.split()
            if len(parts) == 0 or parts[0][0] == '#':
                # Ignore comments and blank lines
                continue
            if len(parts) != 2:
                raise ConfigurationError("Error in routes file: %s" % line)
            path, destination = parts
            if ':' in destination:
                # Responder explicitly specified
                responder_name, extra = destination.split(':', 1)
                responder_type = responder_types.get(responder_name, None)
                if responder_type is None:
                    raise ConfigurationError("Invalid destination '%s' in routes file" % destination)
                responder = responder_type(extra)
            else:
                # Default to PageResponder if there's no ':' in the destination
                responder = PageResponder(destination)
            for p, r in responder.get_routes(path): # FIXME: Better names for p and r
                rule = Rule(p, endpoint=r, methods=r.methods)
                self.map.add(rule)
        self.map.update()

    def dispatch(self, environ):
        try:
            request = Request(environ)
            urls = self.map.bind_to_environ(environ)
            responder, args = urls.match()
            with Context(self.app, environ, request, args) as context:
                for hook in self.app.get_hook_functions('pre-request'):
                    hook(context)
                context.response = responder(context)
                for hook in self.app.get_hook_functions('post-request'):
                    context.response = hook(context) or context.response
            return context.response
        
        # HTTPExceptions are returned as the response, while any other 
        # exceptions are re-raised to be either caught by the in-browser debugger
        # or generate a 500 response.
        except HTTPException, e:
            return e

class Responder(object):
    def get_routes(self, path):
        return [(path, self)]
        
# FIXME: Move this somewhere and import it
class WidgetEvent(object):
    def __init__(self, data):
        event = json.loads(data)
        # FIXME: Don't update from keys beginning with '__' (or store event and implement __getitem__)
        self.__dict__.update(event)

class PageResponder(Responder):
    methods = ['GET', 'POST']
    
    def __init__(self, class_name):
        self.cls = import_string(class_name)
    
    def dispatch(self, context):
        page = self.cls(context)
        response = page.generate()
        return response
    dispatch.methods = ['GET', 'POST']
    
    def dispatch_alt_post(self, context):
        post_type = context.args.pop('_dx_post_type', None)
        # FIXME: Handle None
        page = self.cls(context)
        method = getattr(page, 'POST_%s' % post_type, None)
        # FIXME: Handle None
        response = method(**context.args)
        return response
    dispatch_alt_post.methods = ['POST']
    
    def dispatch_widget_callback(self, context):
        args = context.args
        widget_name = args.pop('_dx_widget')
        callback_name = args.pop('_dx_callback')

        # Recreate a Page instance and get an event handler method from it
        page = self.cls(context)
        handler = getattr(page, 'on_%s_%s' % (widget_name, callback_name), None)
        if handler is None:
            return JsonResponse({'status': 'error', 'text': "Missing handler"})

        event = WidgetEvent(context.request.data) # FIXME: Check content type and length
        # assert context.session.check_csrf_token(event.csrf_token) # FIXME: Throw something better
        # FIXME: Re-enable CSRF token checking when session is working properly
        response_data = handler(event, **args) or {}
        # FIXME: Is the status needed? Could just use HTTP status...
        return JsonResponse({'status': 'ok', 'script': response_data})
    dispatch_widget_callback.methods = ['POST']
    
    def get_routes(self, path):
        return [
            (path, self.dispatch),
            ('%s;<_dx_post_type>' % path, self.dispatch_alt_post),
            ('%s;<_dx_widget>/<_dx_callback>' % path, self.dispatch_widget_callback)
        ]

class TemplateResponder(Responder):
    methods = ['GET']
    
    def __init__(self, template, mimetype='text/html'):
        self.template_name = template
        self.mimetype = mimetype

    def __call__(self, context):
        template = context.app.templates.get_template(self.template_name)
        return Response(template.render({
            'request': context.request
        }), mimetype=self.mimetype)

class RedirectResponder(object):
    methods = ['GET']
    
    def __init__(self, location, status):
        self.location = location
        self.status = status

    def __call__(self, context):
        return redirect(self.location, self.status)

responder_types = {
    'page': PageResponder,
    'redirect': RedirectResponder,
    'template': TemplateResponder,
}
