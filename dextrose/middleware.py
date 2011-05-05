import os.path
from werkzeug import SharedDataMiddleware, DebuggedApplication

def static_files(app, wsgi):
    return SharedDataMiddleware(wsgi, {
        '/static': os.path.join(app.directory, 'static')
    })

def debugger(app, wsgi):
    return DebuggedApplication(wsgi, evalex=True)
