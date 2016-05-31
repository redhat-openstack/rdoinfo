rdoinfo
=======

`rdoinfo` is a git repository containing information about current
[RDO](https://www.rdoproject.org) releases, packages, maintainers and more,
currently in a single `rdo.yml` YAML file. 

`rdoinfo` python module provided in this repo is needed for parsing and
validating the info file.

### Updating the info

Run `verify.py` script for basic sanity check on the `rdo.yml` info file.
Use `git-review` to propose a change.


### Usage


`rdoinfo` is a dynamic information source so you probably want some mechanism
to sync latest from github and import the `rdoinfo` parser module in order to
have up-to-date RDO information.

See `rdoinfo/__init__.py:parse_info_file` function or `verify.py` script to
get an idea what's going on.

[rdopkg](https://github.com/redhat-openstack/rdopkg) provides
`rdopkg.actionmods.rdoinfo` [module](https://github.com/redhat-openstack/rdopkg/blob/master/rdopkg/actionmods/rdoinfo.py)
which can fetch this repo for you (into `~/.rdopkg/rdoinfo` by default), keep
it up-to-date, easily import the parser and give you the parsed info
structure.

```python
from rdopkg.actionmods import rdoinfo

inforepo = rdoinfo.get_default_inforepo()
inforepo.init()
info = inforepo.get_info()
```

Projects that use `rdoinfo`:

 * [rdopkg](https://github.com/redhat-openstack/rdopkg)
 * [DLRN](https://github.com/openstack-packages/DLRN)
