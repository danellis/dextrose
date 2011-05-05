from mongoengine import connect

class MongoExtension(object):
    def __init__(self, app, config):
        host = config['host']
        database = config['database']
        connect(database, host=host)
