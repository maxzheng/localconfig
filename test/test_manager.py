import os
import re
from StringIO import StringIO
import tempfile

import pytest

from localconfig.manager import LocalConfig, NoSectionError, DuplicateSectionError, NoOptionError


TEST_CONFIG = """\
# Section used for type testing
[types]

# An int value
int = 1

# A float value
float = 2.0

# A long value
long = 3L

# A mid-commented out
# comment = value

# A bool value
true = True

# A false bool value
false = False

# A None value
none = None

# A string value
string-value = Value

# A commented out value
# comment = value


####################################################
# Another section
# with multiline comments
####################################################
[another-section]

multi_line = This line spans multiple lines and
    will be written out as such. It will wrap
    where it originally wrapped.

# Comment at the end
"""
COMPACT_TEST_CONFIG = """\
# Section used for type testing
[types]
# An int value
int: 1
# A float value
float: 2.0
# A long value
long: 3L
# A mid-commented out
# comment = value

# A bool value
true: True
# A false bool value
false: False
# A None value
none: None
# A string value
string-value: Value
# A commented out value
# comment = value


####################################################
# Another section
# with multiline comments
####################################################
[another-section]
multi_line: This line spans multiple lines and
  will be written out as such. It will wrap
  where it originally wrapped.
# Comment at the end
"""


@pytest.fixture
def config():
  config = LocalConfig()
  config.read(TEST_CONFIG)
  return config


class TestLocalConfig(object):
  def test_read(self, config):
    assert config.types.int == 1
    assert config.types.float == 2.0
    assert config.types.long == 3L
    assert config.types.true == True
    assert config.types.false == False
    assert config.types.none is None
    assert config.types.string_value == 'Value'

    assert config.another_section.multi_line == \
      'This line spans multiple lines and\nwill be written out as such. It will wrap\nwhere it originally wrapped.'

    with pytest.raises(NoSectionError):
      config.no_section
    with pytest.raises(NoOptionError):
      config.types.no_key

    assert {
      ('types', 'string-value'): '# A string value',
      ('types', 'int'): '# An int value',
      ('types', 'float'): '# A float value',
      ('types', 'long'): '# A long value',
      ('types', 'true'): '# A mid-commented out\n# comment = value\n\n# A bool value',
      ('types', 'false'): '# A false bool value',
      ('types', 'none'): '# A None value',
      'another-section': '# A commented out value\n# comment = value\n\n\n####################################################\n# Another section\n# with multiline comments\n####################################################',
      'types': '# Section used for type testing',
      'LAST_COMMENT_KEY': '# Comment at the end\n'
    } == config._comments

    config = LocalConfig()
    config.read(StringIO(TEST_CONFIG))
    assert 'types' in config

    assert [('multi_line', 'This line spans multiple lines and\nwill be written out as such. '
                           'It will wrap\nwhere it originally wrapped.')] == list(config.items('another-section'))
    assert list(config.items('another-section')) == list(config.items('another_section'))

  def test_read_sources(self):
    last_source_path = os.path.join(os.path.dirname(__file__), 'last_source.cfg')
    config = LocalConfig(last_source_path)

    second_source = StringIO('[sources]\nsecond_source = second\nsource = second')
    assert config.read([TEST_CONFIG, second_source, 'non-existing-file.cfg'])

    third_source_path = os.path.join(os.path.dirname(__file__), 'third_source.cfg')
    with open(third_source_path) as fp:
      assert config.read(fp)

    assert len(config._sources) == 4
    assert config._sources_read == False

    assert config.types.int == 1
    assert config.sources.second_source == 'second'
    assert config.sources.third_source == 'third'
    assert config.sources.source == 'last'

    assert config._sources_read == True

    assert config.read('[sources]\nsource = updated')

    assert config.sources.source == 'updated'

    assert not config.read('non-existing-file.cfg')

  def test_write(self, config):
    temp_file = os.path.join(tempfile.gettempdir(), 'saved-localconfig')
    try:
      config.save(temp_file)
      saved_config = open(temp_file).read()
      assert TEST_CONFIG == saved_config

      config2 = LocalConfig(last_source=temp_file)
      config2.read('[types]\nint = 5')
      assert TEST_CONFIG == str(config2)

      config.save(temp_file, as_template=True)
      saved_config = open(temp_file).read()
      assert re.sub('^([^#\n])', '# \\1', TEST_CONFIG, flags=re.MULTILINE) == saved_config
    finally:
      if os.path.exists(temp_file):
        os.unlink(temp_file)

  def test_output_style(self):
    config = LocalConfig(kv_sep=': ', indent_spaces=2, compact_form=True)
    config.read(TEST_CONFIG)
    assert COMPACT_TEST_CONFIG == str(config)

  def test_set(self, config):
    assert config.types.int == 1
    config.types.int = 4
    assert config.types.int == 4

    config.types.yes = True
    assert config.types.yes == True

    assert 'yes = True' in str(config)

  def test_sep(self):
    config = LocalConfig(kv_sep=': ')
    config.read(TEST_CONFIG)
    assert 'int: 1' in str(config)

  def test_iter(self, config):
    assert list(config) == ['types', 'another-section']
    assert [
      ('int', 1),
      ('float', 2.0),
      ('long', 3L),
      ('true', True),
      ('false', False),
      ('none', None),
      ('string-value', 'Value')] == list(config.types)
    assert {
      'false': False,
      'none': None,
      'string-value': 'Value',
      'int': 1,
      'float': 2.0,
      'long': 3L,
      'true': True} == dict(config.types)

  def test_add_section(self, config):
    config.add_section('New Section', comment='Comment for\n  new section')
    config.new_section.value = 1
    assert '# Comment for\n#   new section\n[New Section]' in str(config)

    with pytest.raises(DuplicateSectionError):
      config.add_section('another-section')
