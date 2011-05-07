#!/usr/bin/env python
import os, argparse
from werkzeug.utils import import_string
from dextrose.application import load_application
from dextrose.utils import import_module
from dextrose.compile import StaticFileCompiler, SassCompiler, CoffeeScriptCompiler

class Command(object):
    def __init__(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        self.add_arguments(parser)
        parser.set_defaults(func=self.run)
    
    def add_arguments(self, parser):
        pass

class RunserverCommand(Command):
    name = 'runserver'
    help = "Run the development server"
    
    def run(self, args):
        from werkzeug.serving import run_simple
        app = load_application(args.package, args.environment)
        wsgi = app.wsgi
        for middleware in app.config['middleware']:
            factory = import_string(middleware)
            wsgi = factory(app, wsgi)
        compiler = StaticFileCompiler([SassCompiler, CoffeeScriptCompiler])
        static_files = compiler.compile_all(os.path.join(app.directory, 'static'))
        run_simple(
            'localhost', 5000, wsgi,
            use_reloader=args.reloader, use_debugger=True, use_evalex=True,
            threaded=False, processes=1, extra_files=static_files
        )
    
    def add_arguments(self, parser):
        parser.add_argument('--no-reloader', action='store_false', dest='reloader')

class ShellCommand(Command):
    name = 'shell'
    help = "Run IPython with an application context"
    
    def run(self, args):
        from IPython.Shell import IPShellEmbed
        from werkzeug import Client, EnvironBuilder
        from dextrose.context import Context
        from dextrose.http import Response
        app = load_application(args.package, args.environment)
        environ_builder = EnvironBuilder()
        environ = environ_builder.get_environ()
        request = environ_builder.get_request()
        client = Client(app, Response)
        with Context(app, environ, request, {}) as context:
            banner="Dextrose IPython shell\n%s" % args.package
            shell = IPShellEmbed(banner=banner, argv=[
                '-prompt_in1', '%s> ' % args.package,
                '-prompt_in2', '%s... ' % (' ' * (len(args.package) - 3)),
                '-prompt_out', '=> '
            ])
            shell(global_ns={}, local_ns={
                'app': app,
                'environ': environ,
                'client': client,
                'context': context
            })

class CompileCommand(Command):
    name = 'compile'
    help = "Compile static files"
    
    def run(self, args):
        module = import_module(args.package)
        directory = os.path.dirname(module.__file__)
        compiler = StaticFileCompiler([SassCompiler, CoffeeScriptCompiler])
        compiler.compile_all(os.path.join(directory, 'static'))

def main():
    parser = argparse.ArgumentParser(prog='dx')
    parser.add_argument('--version', action='version', version='v0.0.0')
    parser.add_argument('-e', '--environment', action='store', default='development')
    parser.add_argument('package', action='store', help="Application package name")
    subparsers = parser.add_subparsers(title="commands", help="command-specific help")
    
    RunserverCommand(subparsers)
    ShellCommand(subparsers)
    CompileCommand(subparsers)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
