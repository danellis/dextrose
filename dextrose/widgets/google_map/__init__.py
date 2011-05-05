from sqlalchemy.orm.exc import NoResultFound
from dextrose.context import Context
from dextrose.http import Response
from dextrose.component import Dependency

class Widget(object):
    pass

class GoogleMap(Widget):
    templates = Dependency('jinja')
    
    def __init__(self, size):
        self.size = size
        
    def __call__(self, context, center=(0,0), markers=None):
        template = self.templates.get('recollectives.widgets.google_map:widget.html')
        return template.render({
            'id': 'dx-widget-gmap',
            'markers': markers or [],
            'center': center
        })
