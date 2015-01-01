localconfig
===========

A simplified interface to ConfigParser using dot notion with data type / comment support.

Design Goals
============

* Simple access to config using dot notion and iterators
* Backward/forward compatible ini format as `ConfigParser`_ (as that is used as the backend)
* Data type support by intelligently guessing the data types based on value on read.
* Multiple data source input (read from string, file pointer, or file)
* Full comment support / retention on save

.. _ConfigParser: https://docs.python.org/2/library/configparser.html

How to Use
==========

To install::

    pip install localconfig

Let's say we have a script named 'program' with the following config in ~/.config/program::

    [Web Server]
    # Server host
    host = 0.0.0.0

    # Server port
    port = 8080

To read the config, simply do:

.. code-block:: python

    from localconfig import config

    start_server(config.web_server.host, config.web_server.port)

    # Or if the config is in docstring:
    # config.read(__doc__)
    #
    # Or if the config file is elsewhere::
    # config.read('/etc/path/to/config.ini')

Now, let's do some inspection:

.. code-block:: python

    # Iterate over sections
    for section in config:
      print section                   # web_server

    sections = list(config)           # ['web_server']

    # Iterate over items
    for key, value in config.web_server:
      print key, value                # host 0.0.0.0
                                      # port 8080

    items = list(config.web_server)   # [('host', '0.0.0.0'), ('port', 8080)]
    items = dict(config.web_server)   # {'host': '0.0.0.0', 'port': 8080}

To add a section and set a value:

.. code-block:: python

    config.add_section('App Server', comment='Settings for application server')
    config.app_server.host = 'localhost'

    # Use `set` if you want to set a comment
    config.set('App Server', 'port', 9090, comment='App server port')

To write the config:

.. code-block:: python

    config.save()

    # Or simply get the config as a string:
    # config_str = str(config)
    #
    # Or save to a different location:
    # config.save('/path/to/save/to.ini')

If we open ~/.config/program now, we would see::

    [Web Server]
    # Server host
    host = 0.0.0.0

    # Server port
    port = 8080

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
long    3L
bool    true false yes no on off (case insensitive)
None    none (case insensitive)
str     Any other value not matched by above
======= ===========================================

Contribute / Report Bugs
========================

Github project: https://github.com/maxzheng/localconfig

Report issues/bugs: https://github.com/maxzheng/localconfig/issues
