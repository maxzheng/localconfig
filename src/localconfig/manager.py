import os
import re
import sys
import textwrap

from ConfigParser import RawConfigParser, SafeConfigParser, NoSectionError
from StringIO import StringIO

from localconfig.utils import is_float, is_int, is_bool, is_config, CONFIG_KEY_RE, to_bool

NON_ALPHA_NUM = re.compile('[^A-Za-z0-9]')


class DotNotionConfig(object):
  """
  Wrapper for ConfigParser that allows configs to be accessed thru a dot notion method with data type support.
  """

  def __init__(self, user_source=None, interpolation=False):
    """
    :param file/str user_source: User config file name. This source is only read when an attempt to read a config
                                 value is made (delayed reading). Defaults to ~/.config/<PROGRAM_NAME> (if available)
    :param bool interpolation: Support interpolation (use SafeConfigParser instead of RawConfigParser)
    """
    if not user_source and sys.argv:
      user_source = os.path.expanduser(os.path.join('~', '.config', os.path.basename(sys.argv[0])))

    #: User config file name
    self.user_source = user_source

    #: Indicate if `self.user_source` has been read
    self._user_source_read = False

    #: Parser instance from ConfigParser that does the underlying config parsing
    self.parser = SafeConfigParser() if interpolation else RawConfigParser()

    #: A dict that maps (section, key) to its comment.
    self.comments = {}

    #: A dict that maps dot notation section.key to its actual (section, key)
    self.dot_keys = {}

  @classmethod
  def to_dot_key(cls, section, key=None):
    """ Return the section and key in dot notation format. """
    if key:
      return (NON_ALPHA_NUM.sub('_', section), NON_ALPHA_NUM.sub('_', key))
    else:
      return NON_ALPHA_NUM.sub('_', section)

  def read(self, source=None):
    """
    Reads and parses the config source

    :param file/str source: Config source string, file name, or file pointer.
    """

    if isinstance(source, str) and is_config(source):
      source_fp = StringIO(source)
    elif isistance(source, file):
      source_fp = source
    else:
      source_fp = open(source)

    self.parser.readfp(source_fp)
    self._parse_extra(source_fp)

  def save(self, target_file=None, as_template=False, kv_sep=' = '):
    """
    Save the config

    :param str target_file: File to save to. Defaults to `self.user_source`
    :param bool as_template: Save the config with all keys and sections commented out for user to modify
    :param str kv_sep: Separator for key and value
    """
    if not target_file:
      target_file = self.user_source

    with open(target_file, 'w') as fp:
      for section in self.parser.sections():
        if section in self.comments:
          fp.write(self.comments[section])
        fp.write('[%s]\n' % section)

        for key, value in self.parser.items(section):
          if (section, key) in self.comments:
            fp.write(self.comments[(section, key)])
          fp.write('%s%s%s\n\n' % (key, kv_sep, '\n'.join(textwrap.wrap(value, subsequent_indent=4))))

  def _parse_extra(self, fp):
    """ Parse and store the config comments and create maps for dot notion lookup """

    comment = ''
    section = ''

    fp.seek(0)
    for line in fp:
      line = line.rstrip()

      if not line:
        continue

      if line.startswith('#'):  # Comment
        comment += line + '\n'
        continue

      if line.startswith('['):  # Section
        section = line.strip('[]')
        self.dot_keys[self.to_dot_key(section)] = section
        if comment:
          self.comments[section] = comment

      elif CONFIG_KEY_RE.match(line):  # Config
        key = line.split('=', 1)[0].strip()
        self.dot_keys[self.to_dot_key(section, key)] = (section, key)
        if comment:
          self.comments[(section, key)] = comment

      comment = ''

  def get(self, section, key, default=None):
    """
    Get config value with data type transformation

    :param str section: Section to get config for
    :param str key: Key to get config for
    :param default: Default value for key
    :return: Value for the section/key or `default` if it does not exist.
    """
    if not self._user_source_read:
      if os.path.exists(self.user_source):
        self.read(self.user_source)
      self._user_source_read = True

    try:
      value = self.parser.get(section, key)
    except Exception:
      return default

    if is_int(value):
      return int(value)
    elif is_float(value):
      return float(value)
    elif is_bool(value):
      return to_bool(value)
    else:
      return value

  def _dot_get(self, section, key, default=None):
    """ Same as :meth:`self.get` except the section / key are using dot notation format from `cls.to_dot_key' """
    if not (section, key) in self.dot_keys:
      return default

    section, key = self.dot_keys[(section, key)]
    return self.get(section, key, default)

  def __getattr__(self, attr):
    if attr in self.dot_keys:
      return SectionAccessor(self, attr)
    elif ('DEFAULT', attr) in self.dot_keys:
      return self._dot_get('DEFAULT', attr)
    raise NoSectionError(attr)


class SectionAccessor(object):
  instances = {}

  def __new__(cls, config, section):
    if (config, section) in cls.instances:
      return cls.instances[(config, section)]
    else:
      return super(SectionAccessor, cls).__new__(cls, config, section)

  def __init__(self, config, section):
    self.config = config
    self.section = section

  def __getattr__(self, attr):
    return self.config._dot_get(self.section, attr)
