from __future__ import absolute_import
from redis.client import Redis
from dextrose.component import register_singleton

class RedisExtension(object):
    def __init__(self, app, config):
        if 'host' not in config:
            raise ConfigurationError("Redis extension needs 'host' configured")
        if 'password' not in config:
            raise ConfigurationError("Postmark extension needs 'password' configured")
        host = config['host']
        password = config['password']
        redis = Redis(host=host, password=password)
        register_singleton(redis, 'redis')
