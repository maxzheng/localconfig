Version 1.1.3
================================================================================

* Fix RST doc format
* Add note about config read order
* Test py37
* Skip setting last source if run by pytest
* Fix typo

Version 1.1.2
--------------------------------------------------------------------------------

* Allow user to specify custom interpolation instance

Version 1.1.1
--------------------------------------------------------------------------------

* Remove test concurrency and change default env to cover,style

Version 1.1.0
--------------------------------------------------------------------------------

* Add support for DEFAULT section
* Fix style issues
* Fix tox.ini
* Switch to 4 space indents

Version 1.0.2
================================================================================

* Switch to use configparser.read_file
* Update tox.ini

Version 1.0.1
--------------------------------------------------------------------------------

* Migrate to Python 3.x

Version 0.4.2
--------------------------------------------------------------------------------

* Return None instead of raising NoSectionError/NoOptionError
* Add long description / url
* Update tox.ini

Version 0.4.1
--------------------------------------------------------------------------------

* Update tox.ini

* Update tox.ini to run test by default

* Ensure last source isn't set to empty string by checking sys.arg[0]
  And skip reading last source when it isn't set.

* Remove ln whitelist from tox

* Remove activate symlink

* Update doc


Version 0.4.0
--------------------------------------------------------------------------------

* Lazy read configs on access and support list of sources

* Rename DotNotationConfig to LocalConfig


Version 0.3.6
================================================================================

* Fix bug in read for non-existing file


Version 0.3.5
--------------------------------------------------------------------------------

* Only read config file if exists


Version 0.3.4
--------------------------------------------------------------------------------

* Remove __new__ use as it does not work as expected and move SectionAccessor back into DotNotationConfig as private class

* Update changelog

* Add changelog to index


Version 0.3.3
--------------------------------------------------------------------------------

* Add changelog

Version 0.3.2
--------------------------------------------------------------------------------

* Add PyPi package link

