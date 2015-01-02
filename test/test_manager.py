import os
import re
from StringIO import StringIO
import tempfile

import pytest

from localconfig.manager import DotNotationConfig, NoSectionError, DuplicateSectionError, NoOptionError


TEST_CONFIG = """\
# Section used for type testing
[types]

# An int value
int = 1

# A float value
float = 2.0

# A long value
long = 3L

# A bool value
true = True

# A false bool value
false = False

# A None value
none = None

# A string value
string-value = Value

####################################################
# Another section
# with multiline comments
####################################################
[another-section]

multi_line = This line spans multiple lines and
    will be written out as such. It will wrap
    where it originally wrapped.
"""


@pytest.fixture
def config():
  config = DotNotationConfig()
  config.read(TEST_CONFIG)
  return config


class TestDotNotationConfig(object):
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
      ('types', 'true'): '# A bool value',
      ('types', 'false'): '# A false bool value',
      ('types', 'none'): '# A None value',
      'another-section': '####################################################\n# Another section\n# with multiline comments\n####################################################',
      'types': '# Section used for type testing'
    } == config._comments

    config = DotNotationConfig()
    config.read(StringIO(TEST_CONFIG))
    assert 'types' in config

  def test_write(self, config):
    temp_file = os.path.join(tempfile.gettempdir(), 'saved-localconfig')
    try:
      config.save(temp_file)
      saved_config = open(temp_file).read()
      assert TEST_CONFIG == saved_config

      config2 = DotNotationConfig(last_source=temp_file)
      config2.read('[types]\nint = 5')
      assert TEST_CONFIG == str(config2)

      config.save(temp_file, as_template=True)
      saved_config = open(temp_file).read()
      assert re.sub('^([^#\n])', '# \\1', TEST_CONFIG, flags=re.MULTILINE) == saved_config
    finally:
      if os.path.exists(temp_file):
        os.unlink(temp_file)

  def test_set(self, config):
    assert config.types.int == 1
    config.types.int = 4
    assert config.types.int == 4

    config.types.yes = True
    assert config.types.yes == True

    assert 'yes = True' in str(config)

  def test_sep(self):
    config = DotNotationConfig(kv_sep=': ')
    config.read(TEST_CONFIG)
    assert 'int: 1' in str(config)

  def test_iter(self, config):
    assert list(config) == ['types', 'another_section']
    assert [
      ('int', 1),
      ('float', 2.0),
      ('long', 3L),
      ('true', True),
      ('false', False),
      ('none', None),
      ('string_value', 'Value')] == list(config.types)
    assert {
      'false': False,
      'none': None,
      'string_value': 'Value',
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
