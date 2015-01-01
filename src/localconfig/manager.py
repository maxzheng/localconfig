from ConfigParser import RawConfigParser, SafeConfigParser, NoSectionError, DuplicateSectionError, NoOptionError
import os
import re
from StringIO import StringIO
import sys
import textwrap


from localconfig.utils import is_float, is_int, is_long, is_bool, is_none, is_config, CONFIG_KEY_RE, to_bool

NON_ALPHA_NUM = re.compile('[^A-Za-z0-9]')
NO_DEFAULT_VALUE = 'NO-DEFAULT-VALUE'


class DotNotionConfig(object):
  """
  Wrapper for ConfigParser that allows configs to be accessed thru a dot notion method with data type support.
  """

  def __init__(self, last_source=None, interpolation=False, kv_sep=' = '):
    """
    :param file/str last_source: Last config source file name. This source is only read when an attempt to read a
                                 config value is made (delayed reading, hence "last") if it exists.
                                 It is also the default target file location for :meth:`self.save`
                                 Defaults to ~/.config/<PROGRAM_NAME> (if available)
    :param bool interpolation: Support interpolation (use SafeConfigParser instead of RawConfigParser)
    :param str kv_sep: Separator for key and value. Used when saving self as string/file.
    """
    if not last_source and sys.argv:
      last_source = os.path.expanduser(os.path.join('~', '.config', os.path.basename(sys.argv[0])))

    #: User config file name
    self._last_source = last_source

    #: Indicate if `self._last_source` has been read
    self._last_source_read = False

    #: Parser instance from ConfigParser that does the underlying config parsing
    self._parser = SafeConfigParser() if interpolation else RawConfigParser()

    #: A dict that maps (section, key) to its comment.
    self._comments = {}

    #: A dict that maps dot notation section.key to its actual (section, key)
    self._dot_keys = {}

    #: Seperator for key/value. Used for save only.
    self._kv_sep = kv_sep

    #: Cache to avoid transforming value too many times
    self._value_cache = {}

  @classmethod
  def _to_dot_key(cls, section, key=None):
    """ Return the section and key in dot notation format. """
    if key:
      return (NON_ALPHA_NUM.sub('_', section.lower()), NON_ALPHA_NUM.sub('_', key.lower()))
    else:
      return NON_ALPHA_NUM.sub('_', section.lower())

  def _add_dot_key(self, section, key=None):
    """
    :param str section: Config section
    :param str key: Config key
    """
    if key:
      self._dot_keys[self._to_dot_key(section, key)] = (section, key)
    else:
      self._dot_keys[self._to_dot_key(section)] = section

  def read(self, source=None):
    """
    Reads and parses the config source

    :param file/str source: Config source string, file name, or file pointer.
    """

    if isinstance(source, str) and is_config(source):
      source_fp = StringIO(source)
    elif isinstance(source, file) or isinstance(source, StringIO):
      source_fp = source
    else:
      source_fp = open(source)

    self._parser.readfp(source_fp)
    self._parse_extra(source_fp)

  def __str__(self):
    self._read_last_source()

    output = []

    for section in self._parser.sections():
      if section in self._comments:
        output.append(self._comments[section])
      output.append('[%s]\n' % section)

      for key, value in self._parser.items(section):
        if (section, key) in self._comments:
          output.append(self._comments[(section, key)])
        output.append('%s%s%s\n' % (key, self._kv_sep, '\n'.join(textwrap.wrap(value, subsequent_indent='    '))))

    return '\n'.join(output)


  def save(self, target_file=None, as_template=False):
    """
    Save the config

    :param str target_file: File to save to. Defaults to `self._last_source`
    :param bool as_template: Save the config with all keys and sections commented out for user to modify
    """
    if not target_file:
      target_file = self._last_source

    output = str(self)

    if as_template:
      output_tmpl = []
      for line in output.split('\n'):
        if line and not line.startswith('#'):
          line = '# %s' % line
        output_tmpl.append(line)
      output = '\n'.join(output_tmpl)

    with open(target_file, 'w') as fp:
      fp.write(output)

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
        self._add_dot_key(section)
        if comment:
          self._comments[section] = comment.rstrip()

      elif CONFIG_KEY_RE.match(line):  # Config
        key = line.split('=', 1)[0].strip()
        self._add_dot_key(section, key)
        if comment:
          self._comments[(section, key)] = comment.rstrip()

      comment = ''

  def get(self, section, key, default=NO_DEFAULT_VALUE):
    """
    Get config value with data type transformation (from str)

    :param str section: Section to get config for
    :param str key: Key to get config for
    :param default: Default value for key if key was not found.
    :return: Value for the section/key or `default` if it does not exist.
    """
    self._read_last_source()

    try:
      value = self._parser.get(section, key)
    except Exception:
      if default == NO_DEFAULT_VALUE:
        raise
      else:
        return default

    return self._typed_value(value)

  def set(self, section, key, value, comment=None):
    """
    Set config value with data type transformation (to str)

    :param str section: Section to set config for
    :param str key: Key to set config for
    :param value: Value for key. It can be any primitive type.
    :param str comment: Comment for the key
    """
    self._read_last_source()

    if not isinstance(value, str):
      value = str(value)

    self._parser.set(section, key, value)

    self._add_dot_key(section, key)
    if comment:
      self._add_comment(section, comment, key)

  def _read_last_source(self):
    if not self._last_source_read:
      if os.path.exists(self._last_source):
        self.read(self._last_source)
      self._last_source_read = True

  def _typed_value(self, value):
    """ Transform string value to an actual data type of the same value. """
    if value not in self._value_cache:
      new_value = value
      if is_int(value):
        new_value = int(value)
      elif is_float(value):
        new_value = float(value)
      elif is_long(value):
        new_value = long(value)
      elif is_bool(value):
        new_value = to_bool(value)
      elif is_none(value):
        new_value = None
      self._value_cache[value] = new_value

    return self._value_cache[value]

  def _dot_get(self, section, key, default=NO_DEFAULT_VALUE):
    """ Same as :meth:`self.get` except the section / key are using dot notation format from `cls._to_dot_key' """
    if not (section, key) in self._dot_keys:
      if default == NO_DEFAULT_VALUE:
        raise NoOptionError(key, section)
      else:
        return default

    section, key = self._dot_keys[(section, key)]
    return self.get(section, key, default)

  def _dot_set(self, section, key, value):
    """ Same as :meth:`self.set` except the section / key are using dot notation format from `cls._to_dot_key' """
    if (section, key) in self._dot_keys:
      section, key = self._dot_keys[(section, key)]
      self.set(section, key, value)
    else:
      section = self._dot_keys[section]
      self.set(section, key, value)

  def __getattr__(self, section):
    """
    Get a section

    :param str section: Section to get
    :rtype: :class:`_SectionAccessor`
    :raise NoSectionError: if section does not exist
    """
    if section in self._dot_keys:
      return _SectionAccessor(self, section)
    raise NoSectionError(section)

  def __iter__(self):
    self._read_last_source()

    for section in self._parser.sections():
      yield self._to_dot_key(section)

  def add_section(self, section, comment=None):
    """
    Add a section

    :param str section: Section to add
    :raise DuplicateSectionError: if section already exist.
    """
    self._read_last_source()

    if self._to_dot_key(section) in self._dot_keys:
      raise DuplicateSectionError(section)

    self._parser.add_section(section)
    self._add_dot_key(section)
    if comment:
      self._add_comment(section, comment)

  def _add_comment(self, section, comment, key=None):
    """
    Add a comment by prefixing with '# '

    :param str section: Section to add comment to
    :param str comment: Comment to add
    :param str key: Key to add comment to
    """

    if '\n' in comment:
      comment = '\n# '.join(comment.split('\n'))
    comment = '# ' + comment

    if key:
      self._comments[(section, key)] = comment
    else:
      self._comments[section] = comment


class _SectionAccessor(object):
  """
  Provides access (read/write/iter) for a config section.

  This is a private class and it is only outside of DotNotionConfig because `super` doesn't work with
  private class in __new__.
  """
  _instances = {}

  def __new__(cls, config, section):
    if (config, section) in cls._instances:
      return cls._instances[(config, section)]
    else:
      return super(_SectionAccessor, cls).__new__(cls, config, section)

  def __init__(self, config, section):
    self._config = config
    self._section = section

  def __getattr__(self, key):
    """
    Get config value

    :param str key: Config key to get value for
    """
    return self._config._dot_get(self._section, key)

  def __setattr__(self, key, value):
    """
    Set config value

    :param str key: Config key to set value for
    :param str value: Config value to set to
    """
    if key in ['_config', '_section']:
      super(_SectionAccessor, self).__setattr__(key, value)
    else:
      return self._config._dot_set(self._section, key, value)

  def __iter__(self):
    self._config._read_last_source()

    section = self._config._dot_keys[self._section]
    for item in self._config._parser.items(section):
      key, value = item
      key = self._config._to_dot_key(key)
      value = self._config._typed_value(value)
      yield (key, value)
