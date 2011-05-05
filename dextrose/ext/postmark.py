from __future__ import absolute_import
from postmark import PMMail
from dextrose.tasks.postmark import send_mail_task
from dextrose.component import register_singleton
from dextrose import ConfigurationError

def init_extension(app, config):
    app.mailer = Mailer(config)

class PostmarkExtension(object):
    def __init__(self, app, config):
        if 'sender' not in config:
            raise ConfigurationError("Postmark extension needs 'sender' configured")
        if 'api_key' not in config:
            raise ConfigurationError("Postmark extension needs 'api_key' configured")
        component = PostmarkComponent(config['sender'], config['api_key'])
        register_singleton(component, 'postmark')

class PostmarkComponent(object):
    def __init__(self, sender, api_key):
        self.sender = sender
        self.api_key = api_key
    
    def send_mail(self, recipients, subject, body):
        return send_mail_task.delay(self.api_key, self.sender, recipients, subject, body)
