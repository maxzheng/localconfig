import re

CONFIG_KEY_RE = re.compile('[A-Za-z0-9\-\_\.]+\s*=')


def is_float(value):
  return _is_type(value, float)


def is_int(value):
  return _is_type(value, int)


def is_long(value):
  return _is_type(value, long)


def is_bool(value):
  return value.lower() in ['true', 'false', 'yes', 'no', 'on', 'off']


def to_bool(value):
  return value.lower() in ['true', 'yes', 'on']


def is_config(value):
  return '\n' in value or CONFIG_KEY_RE.match(value)


def _is_type(value, type):
  try:
    type(value)
    return True
  except Exception:
    return False
