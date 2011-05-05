from dextrose.application import load_application

def application(environ, start_response):
    app_package = environ['dx.application']
    environment = environ['dx.environment']
    application = load_application(app_package, environment)
    return application.wsgi(environ, start_response)
