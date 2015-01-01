import os
import tempfile

from localconfig.manager import DotNotionConfig


TEST_CONFIG = """
# Default config
[DEFAULT]
no_section = 1

# Section used for type testing
[types]
# An int value
int = 1

# A float value
float = 2.0

# A bool value
true = True

# A false bool value
false = False

# A string value
string-value = Value

# Another section
# with multiline comments
[another-section]
multi_line = This line spans
  multiple lines and will be
  written out as such.
"""


class TestDotNotationConfig(object):
  def test_read(self):
    config = DotNotionConfig()
    config.read(TEST_CONFIG)
    assert config.no_section == 1

    assert config.types.int == 1
    assert config.types.float == 2.0
    assert config.types.true == True
    assert config.types.false == False
    assert config.types.string_value == 'Value'

    assert config.another_section.multi_line == 'This line spans\nmultiple lines and will be\nwritten out as such.'

    assert config.comments == {
      ('types', 'string-value'): '# A string value\n',
      'DEFAULT': '# Default config\n',
      ('types', 'int'): '# An int value\n',
      ('types', 'float'): '# A float value\n',
      ('types', 'true'): '# A bool value\n',
      'another-section': '# Another section\n# with multiline comments\n',
      ('types', 'false'): '# A false bool value\n',
      'types': '# Section used for type testing\n'
    }

  def test_write(self):
    config = DotNotionConfig()
    config.read(TEST_CONFIG)

    temp_file = os.path.join(tempfile.gettempdir(), 'saved-localconfig')
    try:
      config.save(temp_file)
      saved_config = open(temp_file).read()
      assert TEST_CONFIG == saved_config
    finally:
      if os.path.exists(temp_file):
        os.unlink(temp_file)
