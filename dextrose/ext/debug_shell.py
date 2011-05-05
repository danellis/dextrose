import __builtin__
from IPython.Shell import IPShellEmbed

class DebugShellExtension(object):
    def __init__(self, app, config):
        __builtin__.debug_shell = IPShellEmbed()

