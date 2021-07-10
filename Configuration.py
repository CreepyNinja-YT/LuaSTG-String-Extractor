import configparser

"""
Just little configuration class.
(I think I should rather extract other classes than that...)

Made by CreepyNinja. Have fun~
"""


class Configuration:
    def __init__(self, configfile='config.ini'):
        config = configparser.RawConfigParser()
        config.read(configfile)
        if 'Config' not in config:
            raise AssertionError('Config session not found in file')
        self.properties = config['Config']

    def get(self, key, default=None):
        value = self.properties.get(key)
        if value is None:
            if default is None:
                raise KeyError(f'Key {key} not found in properties')
            else:
                return default
        return value

    def get_if_null(self, key, value, default=None):
        if value is None:
            return self.get(key, default)
        else:
            return value
