localconfig
===========

A simplified interface to `ConfigParser`_ using dot notion with data type / comment support.

Feature Summary
===============

* Simple access to config using dot notion and iterators
* Full compatibility with `ConfigParser`_ ini formats (as that is used as the backend)
* Data type support by intelligently guessing the data types based on value on read.
* Multiple config source input (read from string, file pointer, file, or list of them)
* Full comment support / retention on save
* Lazy reading of config sources for performance (only read when a config value is accessed)

.. _ConfigParser: https://docs.python.org/3/library/configparser.html

Quick Start Tutorial
====================

To install::

    pip install localconfig

Let's say we have a script named `program` with the following config in `~/.config/program`:

.. code-block:: ini

    [Web Server]
    # Server host
    host = 0.0.0.0

    # Server port
    port = 8080

    # Debug logging
    debug = off

To read the config, simply do:

.. code-block:: python

    from localconfig import config

    start_server(config.web_server.host, config.web_server.port, config.web_server.debug)

    # Or use get method:
    # start_server(config.get('Web Server', 'host'),
    #              config.get('Web Server', 'port'),
    #              config.get('web_server', 'debug'))  # Yes, 'web_server' also works here!
    #
    # Or if the config is in docstring, read from it:
    # config.read(__doc__)
    #
    # Or if the config file is elsewhere:
    # config.read('/etc/path/to/config.ini')  # Non-existing file is ignored
    #
    # Or read from a list of sources
    # config.read(['string config', file_path, file_pointer, io.StringIO('config')])
    #
    # Or create another instance for another config:
    # from localconfig import LocalConfig
    # config2 = LocalConfig('/etc/path/to/another/config.ini')

Configs are read in the order they are called using `config.read()`, but the config file passed to the `LocalConfig()`
constructor (defaults to `~/.config/$script_name`) will be read last before the first access to config values, which
allows us to read configs from various locations, like default configs from a string that is checked in with the code,
while allowing them to be overrriden from the config file that is passed to the constructor.

Now, let's do some inspection:

.. code-block:: python

    # Iterate over sections and their keys/values
    for section in config:
      print(section)                   # Web Server

      for key, value in config.items(section):
        print(key, value, type(value)) # host 0.0.0.0 <type 'str'>
                                       # port 8080 <type 'int'>
                                       # debug False <type 'bool'>

    sections = list(config)            # ['Web Server']

    # Iterate over keys/values
    for key, value in config.web_server:
      print(key, value, type(value))    # Same output as above config.items()

    items = list(config.web_server)    # [('host', '0.0.0.0'), ('port', 8080), ('debug', False)]
    items = dict(config.web_server)    # {'host': '0.0.0.0', 'port': 8080, 'debug': False}

    # Check if a section or key is set - any non-existing section or key defaults to None.
    if config.web_server or config.no_such_section:
      pass

    if config.web_server and (config.web_server.port or config.web_server.no_such_key):
      pass

To add a section and set a value:

.. code-block:: python

    config.add_section('App Server', comment='Settings for application server')
    config.app_server.host = 'localhost'

    # Use `set` if you want to set a comment
    config.set('App Server', 'port', 9090, comment='App server port')

    # Set value for the DEFAULT section (default value for all other sections)
    config.env = 'prod'

To write the config:

.. code-block:: python

    config.save()

    # Or simply get the config as a string:
    # config_str = str(config)
    #
    # Or save to a different location:
    # config.save('/path/to/save/to.ini')

If we open `~/.config/program` now, we would see::

    [DEFAULT]

    env = prod


    [Web Server]

    # Server host
    host = 0.0.0.0

    # Server port
    port = 8080

    # Debug logging
    debug = off


    # Settings for application server
    [App Server]

    host = localhost

    # App server port
    port = 9090

Supported Data Types
====================

Data type is guessed based on the value and converted on read.

The following types are supported:

======= ===========================================
Type    Example Value
======= ===========================================
int     1
float   2.0
bool    true false yes no on off (case insensitive)
None    none (case insensitive)
str     Any other value not matched by above
======= ===========================================

Remote Config
=============

Check out: https://pypi.python.org/pypi/remoteconfig

More
====

| Documentation: http://localconfig.readthedocs.org/
|
| PyPI Package: https://pypi.python.org/pypi/localconfig
| GitHub Source: https://github.com/maxzheng/localconfig
| Report Issues/Bugs: https://github.com/maxzheng/localconfig/issues
|
| Connect: https://www.linkedin.com/in/maxzheng
| Contact: maxzheng.os @t gmail.com
