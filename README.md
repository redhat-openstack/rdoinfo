rdoinfo
-------

`rdoinfo` is a git repository containing information about current RDO
releases, packages, maintainers and more in a `rdo.yml` YAML file.

Also included is simple `rdoinfo` python module for parsing and validating the
info file. See `rdoinfo/__init__.py:parse_info_file` function or
`verify.py` script for example of usage.

Run `verify.py` script for basic sanity check on the `rdo.yml` info file
before submitting changes.
