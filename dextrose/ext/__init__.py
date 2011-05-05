from dextrose import ConfigurationError

def check_config_keys(extension, config, keys):
    for key in keys:
        if key not in config:
            raise ConfigurationError("%s extension needs '%s' configured" % (extension, key))
