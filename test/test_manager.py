import os
import re
import tempfile

from localconfig.manager import DotNotionConfig


TEST_CONFIG = """\
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

####################################################
# Another section
# with multiline comments
####################################################
[another-section]

multi_line = This line spans multiple lines and will be written out as such. When
    it is long enough, it will wrap.
"""


class TestDotNotationConfig(object):
  def test_read(self):
    config = DotNotionConfig()
    config.read(TEST_CONFIG)

    assert config.types.int == 1
    assert config.types.float == 2.0
    assert config.types.true == True
    assert config.types.false == False
    assert config.types.string_value == 'Value'

    assert config.another_section.multi_line == \
      'This line spans multiple lines and will be written out as such. When\nit is long enough, it will wrap.'

    assert {
      ('types', 'string-value'): '# A string value',
      ('types', 'int'): '# An int value',
      ('types', 'float'): '# A float value',
      ('types', 'true'): '# A bool value',
      'another-section': '####################################################\n# Another section\n# with multiline comments\n####################################################',
      ('types', 'false'): '# A false bool value',
      'types': '# Section used for type testing'
    } == config.comments

  def test_write(self):
    config = DotNotionConfig()
    config.read(TEST_CONFIG)

    temp_file = os.path.join(tempfile.gettempdir(), 'saved-localconfig')
    try:
      config.save(temp_file)
      saved_config = open(temp_file).read()
      assert TEST_CONFIG == saved_config

      config.save(temp_file, as_template=True)
      saved_config = open(temp_file).read()
      assert re.sub('^([^#\n])', '# \\1', TEST_CONFIG, flags=re.MULTILINE) == saved_config
    finally:
      if os.path.exists(temp_file):
        os.unlink(temp_file)
