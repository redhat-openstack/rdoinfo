Introduction to rdoinfo
=======================

`rdoinfo` is a git repository containing information about current
`RDO <https://www.rdoproject.org>`_ releases, packages, maintainers and more.
Currently main YAML files, `rdo.yml`, `deps.yaml`, `tags.yaml`,
`buildsys-tags.yaml` contains:

* *rdo.yml* contains information of RDO releases, OpenStack packages included in RDO Trunk
            repositories and package configurations used by these packages.

* *deps.yml* contains metadata for general purpose dependencies which are external requirements
             for OpenStack services and don't exist in CentOS core repositories. These packages are included
             in RDO CloudSIG repos but not in RDO Trunk.

* *buildsys-tags* are used to specify the tagged builds in RDO CloudSIG repos for each
                  tag in CentOS Build System (CBS). It contains a set of mappings where the key is the
                  CBS tag name and the value is the package NVR included in the tag.

* *tags.yaml* attribute is used by the RDO Trunk builders to determine which releases we need
              to build a package for, and if we need to use some release-specific information for
              a project.


`rdoinfo` repository have two main directories:

* *buildsys-tags* are used to specify the tagged builds in RDO CloudSIG repos for each
  tag in CentOS Build System (CBS). In this dir, all files have specific convention:
  cloud - `CentOS release number` -openstack- `release` - `phase` where:

    * *CentOS release number* - since Ussuri release, it will be 7 or 8
    * *release*, official Openstack release name as ussuri, train, stein, etc.
      Available Openstack release names you can find here [1]_.
    * *phase* - name of fallowing phase:
        * *candidate* phase is assigned to packages to be rebuilt in CBS but not pushed
          to any RDO repository.
        * *el7-build* (only available for Rocky and newer releases) is assigned to packages
          that only required to build other packages but are not a runtime requirement
          for any other package.
        * *testing* phase means that the package is used in deployments using RDO Trunk repo
          and published in a testing repo, but not official CloudSIG repository.


In addition to the release names, we can use some special tag:

    * *version-locked* is used to prevent our periodic jobs from proposing updates to
      the source-branch tag in projects managed by the upper-constraints file.

Explaination of buildsys-tags file metadat will be a

Example what metadata is set in buildsys-sys/ files will be explained below.


* *tags* in this dir, each file has the name of Openstack relase.

Example what metadata is set in tags/ yaml files will be explained below.


`rdoinfo` python module provided in this repo is needed for parsing and
validating the info file.


YAML files syntax
-----------------

Each file has its use. Below are examples of metadata per yaml file.


For `rdo.yaml` file:

.. code::YAML
    release:
    ...
    - name: train
      branch: rpm-master
      tags_map: separated_buildreqs
      repos:
      - name: el7
        buildsys: cbs/cloud7-openstack-train-el7
        buildsys-tags:
        - cloud7-openstack-train-el7-build
        - cloud7-openstack-train-candidate
        - cloud7-openstack-train-testing
        - cloud7-openstack-train-release
        distrepos:
        - name: RDO Train el7
          url: http://mirror.centos.org/centos/7/cloud/x86_64/openstack-train/
        - name: CentOS 7 Base
          url: http://mirror.centos.org/centos/7/os/x86_64/
        - name: CentOS 7 Updates
          url: http://mirror.centos.org/centos/7/updates/x86_64/
        - name: CentOS 7 Extras
    ...
    package-default:
      name: python-%(project)s
      distgit: ssh://pkgs.fedoraproject.org/python-%(project)s.git
      patches: http://review.rdoproject.org/r/p/openstack/%(project)s.git
      master-distgit: https://github.com/rdo-packages/%(project)s-distgit.git
      tags:
        ussuri-uc:
        ussuri:
        train:
        stein:
        rocky:
        queens:
        pike:
        ocata:
    ...
    package-configs:
      somepackage:
        name: openstack-%(project)s
        upstream: https://git.openstack.org/openstack/%(project)s
        distgit: https://github.com/rdo-packages/%(project)s-distgit.git
        patches: http://review.rdoproject.org/r/p/openstack/%(project)s.git
        master-distgit: https://github.com/rdo-packages/%(project)s-distgit.git
        review-patches: ssh://review.rdoproject.org:29418/openstack/%(project)s.git
        review-origin: ssh://review.rdoproject.org:29418/openstack/%(project)s-distgit.git
        component: common
        maintainers:
        - null@rdoproject.org
    packages:
    # OpenStack Puppet Modules
    - project: puppet-aodh
      conf: rpmfactory-puppet
    ...
    components:
    - name: common
    - name: compute
    - name: tripleo


Following attributes are assigned to packages:

* *release* section - phase means that is published in the official CloudSIG repository.
                      This phase is only available after a RDO version has been officially released
                      not for the one currently under development.

    * *name:* Openstack release name
    * *branch:* project distgit branch
    * *tags_map:* <<<< FIXME >>>>>
    * *repos* defines main repo name, CBS [2]_ build target tags, repository url for built packages

* *package-default* section - default informatios. If package doesn't include that
                              data, it will be set from this section

    * *name:* package name
    * *distgit:* package distgit repo that include spec files, startup scripts, etc.
    * *patches:* RDO repository that contains required patches for building package
    * *master-distgit:* upstream repository url
    * *tags:* available tags in distgit repository. Usually are named as Openstack releases.

* *package-configs* section - main package metadata that will be used later in packages section
    * *name:* package name
    * *upstream:* upstream repository url
    * *distgit:* package distgit repo that include spec files, startup scripts, etc.
    * *patches:* RDO repository that contains required patches for building package
    * *master-distgit:* upstream repository url <<<< FIXME: difference between distgit and master-distgit >>>>
    * *review-patches:* the RDO project git repository url for package fixes
    * *review-origin:*  the RDO project package distgit git repository
    * *component:* it defines package role
    * *maintainers:* responsible person for update and fix building issues

* *packages:* section - defines all available packages to build
    * *conf:* is defining which package-config should be used to build the package

* *components* section - names of available package role


For `deps.yml` file:

.. code::YAML
    package-configs:
      fedora-dependency:
         # This is the conf for dependencies rebuilt from Fedora distgit
         # and using cbs-tags for automatic tagging
        distgit: https://src.fedoraproject.org/git/rpms/%(project)s.git
        patches:
        master-distgit: https://src.fedoraproject.org/git/rpms/%(project)s.git
        review-patches:
        review-origin:
        tags:
          dependency:
        maintainers:
        - nobody@rdoproject.org
    ...
    packages:
    - project: python-sphinx
      name: python-sphinx
      conf: rdo-dependency
      upstream: https://github.com/sphinx-doc/sphinx

Following attributes are assigned to config in package-config:

* *distgit:*
* *patches: git* repository containing patches applied on packaging
* *master-distgit:* (FIXME: deprecated) git repository containing the distgit for the package, used by dlrn rdoinfo driver.
* *review-patches:* git repository for gerrit reviews for patches applied on packaging
* *review-origin:* git repository for gerrit reviews on distgit
* *tags:* tage name to checkout before packaging
* *maintainers:* username and email of person responsible for the package

And for the *packages*:
* *project:* project name
* *name:* package name
* *conf:* package configuration informations; it is defined in package-configs key
* *upstream:* official project url


For `buildsys-tags/*` file:

.. code::YAML
    packages:
    ...
    - project: ansible-role-chrony
      buildsys-tags:
        cloud7-openstack-train-testing: ansible-role-chrony-1.0.1-1.el7

Following attribues are assigned for e.g. `buildsys-tags/cloud7-openstack-train-testing.yml`

* *project* package project name
* *buildsys-tags* name of CBS [3]_ build tag


For `tags/train.yaml` file:

.. code::YAML
    packages:
    - project: ansible-role-chrony
      tags:
        train:
    ...

 Following attribues are assinged for e.g.: train.yaml file:

* *project:* package project name
* *tags:* Openstack release name


Why it has such architecture
============================

`DLRN can build packages using different upstream branches, not only master.
For example, we have DLRN workers building packages for the Newton and Mitaka
releases. That allows us to test each commit landing to stable/newton and
stable/mitaka before it is part of a release.` [4]_
Before packaging, all described yaml files are merged into one using `rdo-full.yml` file,
so after that DLRN is able to get all required informations. <<<FIXME>>>


Projects that use `rdoinfo`:

    * rdopkg [5]_
    * DLRN [6]_
    * <<<FIXME>>>



Updating rdoinfo
================

rdoinfo is managed using [RDO SoftwareFactory instance] [8]_.
In order to modify it you need to [login using your github account] [9]_. Once your account is created:

1. Clone the rdoinfo repository:

    .. code::bash

        git clone https://review.rdoproject.org/r/rdoinfo

2. Edit the `rdo.yml` or `deps.yml` files with the required changes.
3. Run `tox -e validate` command for basic sanity check.
4. Use `git review` to propose a change.


Usage
=====

`rdoinfo` is a dynamic information source so you probably want some mechanism
to sync latest from github and import the `rdoinfo` parser module in order to
have up-to-date RDO information.

See `rdoinfo/__init__.py:parse_info_file` function or `verify.py` script to
get an idea what's going on.

`rdopkg` [5]_ provides `rdopkg.actionmods.rdoinfo` module [7]_
which can fetch this repo for you (into `~/.rdopkg/rdoinfo` by default), keep
it up-to-date, easily import the parser and give you the parsed info
structure:

  .. code-block::python

    from rdopkg.actionmods import rdoinfo

    inforepo = rdoinfo.get_default_inforepo()
    inforepo.init()
    info = inforepo.get_info()


References
==========

.. [1] http://releases.openstack.org/
.. [2] https://cbs.centos.org/
.. [3] https://github.com/softwarefactory-project/DLRN
.. [4] https://www.rdoproject.org/what/dlrn/
.. [5] https://github.com/redhat-openstack/rdopkg
.. [6] https://github.com/openstack-packages/DLRN
.. [7] https://github.com/redhat-openstack/rdopkg/blob/master/rdopkg/actionmods/rdoinfo.py
.. [8] https://review.rdoproject.org/r/#/q/project:rdoinfo
.. [9] https://review.rdoproject.org/auth/logout
