import json

CONFIG_KEYS = ('client', 'host', 'port')

def load_config(path):
    '''Load the configuration file and return the settings.

       @param path : str
           the path to the configuration file'''

    try:
        config_file = open(path, 'r')
    except IOError:
        raise BaseException('config file does not exist at %s' % path)

    try:
        _config = json.load(config_file)
    except ValueError:
        raise BaseException('invalid JSON in config file at %s' % path)
    finally:
        config_file.close()

    config = dict()
    missing = list()

    for key in CONFIG_KEYS:
        if key not in _config:
            missing.append(key)
        else:
            config[key] = _config[key]

    if missing:
        raise BaseException('config file at %s is missing the following keys: %s' % (path, ', '.join(missing)))

    return config

def write_config(config, path):
    '''Write the configuration to the file at path.

       @param config : dict
           the settings to write
       @param path : str
           the location of the to-be-created config file'''

    missing = list()
    _config = dict()

    for key in CONFIG_KEYS:
        if key not in config:
            missing.append(key)
        else:
            _config[key] = config[key]

    if missing:
        raise BaseException('outgoing configuration is missing the following keys: %s' % ', '.join(missing))

    try:
        config_file = open(path, 'w')
    except IOError:
        raise BaseException('could not open %s for configuration file writing' % path)

    json.dump(_config, config_file, sort_keys=True, indent=4)
    config_file.close()

            

