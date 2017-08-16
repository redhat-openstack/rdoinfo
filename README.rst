Introduction to rdoinfo
=======================

`rdoinfo` is a git repository containing information about current
`RDO <https://www.rdoproject.org>`_ releases, packages, maintainers and more,
currently in two YAML files, `rdo.yml` and `deps.yaml`:

* *rdo.yml* contains information of RDO releases, OpenStack packages included in RDO Trunk
repositores and package configurations used by these packages.
* *deps.yml* contains metadata for general purpose dependencies which are external requirements
for OpenStack services and don't exist in CentOS core repositories. These packages are included
in RDO CloudSIG repos but not in RDO Trunk.

`rdoinfo` python module provided in this repo is needed for parsing and
validating the info file.


YAML files syntax
-----------------

An example of metadata associated to a package is provided here::

    - project: novaclient
      name: python-novaclient
      conf: rpmfactory-client
      upstream: git://git.openstack.org/openstack/python-novaclient
      patches: http://review.rdoproject.org/r/p/openstack/novaclient.git
      distgit: https://github.com/rdo-packages/novaclient-distgit.git
      master-distgit: https://github.com/rdo-packages/novaclient-distgit.git
      review-origin: ssh://review.rdoproject.org:29418/openstack/novaclient-distgit.git
      review-patches: ssh://review.rdoproject.org:29418/openstack/novaclient.git
      tags:
        newton:
          source-branch: 6.0.1
        ocata:
          source-branch: 7.1.2
        pike:
        pike-uc:
          source-branch: 9.0.1
      buildsys-tags:
        cloud7-openstack-newton-release: python-novaclient-6.0.1-1.el7
        cloud7-openstack-newton-testing: python-novaclient-6.0.1-1.el7
        cloud7-openstack-ocata-release: python-novaclient-7.1.0-1.el7
        cloud7-openstack-ocata-testing: python-novaclient-7.1.1-1.el7

Following attributes are assigned to packages:

* *project:* is the name of the upstream project
* *name:* package name
* *conf:* rdoinfo configuration assigned to the project (see attributes inheritance section)
* *maintainers:* The list of package maintainers used as a reference of who takes ownership
  of the package. It does not mean that nobody else can do modifications to the spec, but
  it will be used to notify the owners when a package fails to build.

Git repositories for the package:

* *upstream:* git repository containing the upstream code
* *master-distgit:* git repository containing the distgit for the package, used by DLRN rdoinfo driver.
* *distgit:* (legacy) similar to master-distgit but not longer used by DLRN. It will be deprecated.
* *review-origin:* git repository for gerrit reviews on distgit
* *patches: git* repository containing patches applied on packaging
* *review-patches:* git repository for gerrit reviews for patches applied on packaging

*tags* attribute is used by the RDO Trunk builders to determine which releases we need
to build a package for, and if we need to use some release-specific information for
a project:

* *release* tags, as newton, ocata, pike, queens or queens-uc means that the package will be
  included in the RDO Trunk repo for that specific release.

  * source-branch: inside a release tag defines the git branch, tag or commit will be
    built for the release. In the above example, python-novaclient 6.0.1 will be built
    for Newton, etc...
* In addition to the release names, we can use some special tags:

  * *under-review* is used during the review phase for a new package. Having this tag
    allows our CI jobs to build the package while being reviewed, but prevents RDO
    Trunk builders from adding it to the repos.
  * *version-locked* is used to prevent our periodic jobs from proposing updates to the source-branch tag in projects managed by the upper-constraints file. 

* buildsys-tags: are used to specify the tagged builds in RDO CloudSIG repos for each
  tag in CentOS Build System (CBS). It contains a set of mappings where the key is the
  CBS tag name and the value is the package NVR included in the tag.

  * *version-locked* can be used as buildsys-tag key to disable automatic update by
    periodic job. if a list of CBS tags is assigned to version-locked buildsys-tag,
    only the tags in the list are locked. If it's empty automatic job will ignore the
    package for all tags.


Attributes inheritance in rdoinfo
---------------------------------

rdoinfo has a *package configurations* mechanism to provide different defaults for
package atributes. These configurations define a template for certain fields that follow
a common pattern, such as upstream Git repo or package name. These configurations include:

* rpmfactory-core, for service projects (e.g. Nova, Neutron)
* rpmfactory-client, for Python clients (e.g. python-glanceclient, python-cinderclient)
* rpmfactory-lib, for generic Python libraries (e.g. oslo-sphinx, oslo-messaging)
* rpmfactory-puppet, for Puppet modules
* rpmfactory-tempest-plugin, for tempest plugins packages
* unmanaged-dependency, for dependencies whose distgit is not managed using RDO gerrit instance.

Once you have defined a configuration in your new project section using *conf* atribute,
most of the options are defined for you. Note that any option specified in the package section
will override the option inherited from the configuration.

Updating rdoinfo
----------------

rdoinfo is managed using [RDO SoftwareFactory instance](https://review.rdoproject.org/r/#/q/project:rdoinfo).
In order to modify it you need to [login using your github account](https://review.rdoproject.org/auth/logout). Once your account is created:

1. Clone the rdoinfo repository:

    .. code-block:: bash

        git clone https://review.rdoproject.org/r/rdoinfo

2. Edit the `rdo.yml` or `deps.yml` files with the required changes.

3. Run `verify.py` script for basic sanity check.

4. Use `git review` to propose a change.


Usage
-----


`rdoinfo` is a dynamic information source so you probably want some mechanism
to sync latest from github and import the `rdoinfo` parser module in order to
have up-to-date RDO information.

See `rdoinfo/__init__.py:parse_info_file` function or `verify.py` script to
get an idea what's going on.

`rdopkg <https://github.com/redhat-openstack/rdopkg>`_ provides
`rdopkg.actionmods.rdoinfo module <https://github.com/redhat-openstack/rdopkg/blob/master/rdopkg/actionmods/rdoinfo.py>`_
which can fetch this repo for you (into `~/.rdopkg/rdoinfo` by default), keep
it up-to-date, easily import the parser and give you the parsed info
structure.

.. code-block:: python

    from rdopkg.actionmods import rdoinfo

    inforepo = rdoinfo.get_default_inforepo()
    inforepo.init()
    info = inforepo.get_info()

Projects that use `rdoinfo`:

 * `rdopkg <https://github.com/redhat-openstack/rdopkg>`_
 * `DLRN <https://github.com/openstack-packages/DLRN>`_
