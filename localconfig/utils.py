import re

CONFIG_KEY_RE = re.compile('[A-Za-z0-9\-\_\.]+\s*=')


def is_float(value):
    """ Checks if the value is a float """
    return _is_type(value, float)


def is_int(value):
    """ Checks if the value is an int """
    return _is_type(value, int)


def is_bool(value):
    """ Checks if the value is a bool """
    return value.lower() in ['true', 'false', 'yes', 'no', 'on', 'off']


def is_none(value):
    """ Checks if the value is a None """
    return value.lower() == str(None).lower()


def to_bool(value):
    """ Converts value to a bool """
    return value.lower() in ['true', 'yes', 'on']


def is_config(value):
    """ Checks if the value is possible config content """
    return '\n' in value or CONFIG_KEY_RE.match(value)


def _is_type(value, type):
    try:
        type(value)
        return True
    except Exception:
        return False
