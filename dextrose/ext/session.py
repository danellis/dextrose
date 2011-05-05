import time, random, os
from hashlib import sha256
from werkzeug.utils import import_string
from dextrose.ext import check_config_keys
from dextrose.component import Dependency
from dextrose import ConfigurationError

ONE_WEEK = 604800

def requires_login(fn):
    def decorator(self, *args, **kwargs):
        request = self.request
        if request.session.has_key('user_id'):
            return fn(self, *args, **kwargs)
        else:
            return self.redirect('/login?next=%s' % request.path)
    return decorator

class Session(object):
    cache = Dependency('redis')
    
    def __init__(self, secret, session_id=None, user=None):
        self.secret = secret
        self.session_id = session_id or self._create_session_id()
        self._user = user
        self.is_new = session_id is None
    
    def _get_user(self):
        return self._user
    
    def _set_user(self, user):
        self._user = user
        if user is None:
            self.cache.delete('session.%s' % self.session_id)
        else:
            self.cache.set('session.%s' % self.session_id, user.id)
    
    user = property(_get_user, _set_user)
    
    def _create_session_id(self):
        id_str = "%f%s%f%s" % (
            time.time(), 
            id({}), 
            random.random(),
            os.getpid()
        )
        return sha256(id_str).hexdigest()
    
    def create_csrf_token(self):
        print "CREATING CSRF TOKEN using session_id", self.session_id
        return sha256(self.secret + self.session_id).hexdigest()
    
    def check_csrf_token(self, token):
        print "token =", token
        print "expected =", self.create_csrf_token()
        return token == self.create_csrf_token()

class SessionExtension(object):
    cache = Dependency('redis')
    
    def __init__(self, app, config):
        user_class_name = config.get('user_class', 'User')
        self.user_class = import_string(user_class_name)
        self.cookie_name = config.get('cookie_name', 'SESSION')
        self.domain = config.get('cookie_domain', 'localhost')
        if ':' in self.domain:
            raise ConfigurationError("cookie_domain configuration option should not contain a port")
        self.path = config.get('cookie_path', '/')
        self.expiry = config.get('expiry', ONE_WEEK)
        self.secret = config.get('secret', None)
        if self.secret is None:
            raise ConfigurationError("Session extension needs secret in configuration")
        app.register_hook_function('pre-request', self.pre_request)
        app.register_hook_function('post-request', self.post_request)

    def pre_request(self, context):
        session_id = context.request.cookies.get(self.cookie_name)
        if session_id is None:
            print "1"
            # The request came in without a session cookie, so create a new session
            session = Session(self.secret)
            self.cache.set('session.%s' % session.session_id, 'ANONYMOUS')
        else:
            print "2"
            # The request came in with a session cookie
            user_id = self.cache.get('session.%s' % session_id)
            if not user_id:
                print "3"
                # The session in the cookie isn't valid, so create a new one
                # A new session ID is created to prevent session pinning attacks
                session = Session(self.secret)
                self.cache.set('session.%s' % session.session_id, 'ANONYMOUS')
            else:
                print "4"
                # The session is valid and has a user ID
                user = self.user_class.objects.with_id(user_id)
                session = Session(self.secret, session_id, user)
        self.cache.expire('session.%s' % session.session_id, self.expiry)
        context.session = session
    
    def post_request(self, context):
        # If the session has been created during the processing of the current request,
        # a session ID cookie needs to be set
        if context.session.is_new:
            print "Setting cookie", context.session.session_id
            context.response.set_cookie(
                self.cookie_name,
                context.session.session_id,
                self.expiry, None,
                self.path, self.domain,
                httponly=True
            )
