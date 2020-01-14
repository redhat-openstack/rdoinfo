Introduction to rdoinfo
=======================

`rdoinfo` is a git repository containing information about current
`RDO <https://www.rdoproject.org>`_ releases, packages, maintainers and more.
Currently main YAML files, `rdo.yml`, `deps.yaml`, `tags.yaml`,
`buildsys-tags.yaml` contains:

* *rdo.yml* contains information of RDO releases, OpenStack packages included in RDO Trunk
            repositores and package configurations used by these packages.

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

* *buildsys-tags* in this dir, all files have specific convention:
  `cloud7-openstack` - `release` - `phase` where:

    * *release* tags, as ussuri, train, stein, means that the package will be
      included in the RDO Trunk repo for that specific release.
      Available Openstack release names you can find here.

        * source-branch: inside a release tag defines the git branch, tag or commit will be
          built for the release. In the above example, python-novaclient 6.0.1 will be built
          for Newton, etc...

      In addition to the release names, we can use some special tags:

        * *under-review* is used during the review phase for a new package. Having this tag
          allows our CI jobs to build the package while being reviewed, but prevents RDO
          Trunk builders from adding it to the repos.
        * *version-locked* is used to prevent our periodic jobs from proposing updates to
          the source-branch tag in projects managed by the upper-constraints file.

    * *phase* - name of fallowing phase:

        * *candidate* phase is assigned to packages to be rebuilt in CBS but not pushed
          to any RDO repository.
        * *el7-build* (only available for Rocky and newer releases) is assigned to packages
          that only required to build other packages but are not a runtime requirement
          for any other package.
        * *testing* phase means that the package is used in deployments using RDO Trunk repo
          and published in a testing repo, but not official CloudSIG repository.
        * *release* - phase means that is published in the official CloudSIG repository.
          This phase is only available after a RDO version has been officially released
          not for the one currently under development.

* *tags* in this dir, each file has the name of Openstack relase name.


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


Following attributes are assigned to packages:

* *name:* Openstack release name
* *branch:* project distgit branch
* *tags_map:* FIXME
* *repos* defines main repo name, CBS [1]_ build target tags, repository url for built packages


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
* *buildsys-tags* name of CBS [1]_ build tag


For `tags/train.yaml` file:

.. code::YAML
    packages:
    - project: ansible-role-chrony
      tags:
        train:
    ...

 Following attribues are assinged for e.g.: train.yaml file:

* *project:* package project name
* *tags:* name of


Why it has such architecture
============================

`DLRN can build packages using different upstream branches, not only master.
For example, we have DLRN workers building packages for the Newton and Mitaka
releases. That allows us to test each commit landing to stable/newton and
stable/mitaka before it is part of a release.` [3]_
Before packaging, all described yaml files are merged into one using `rdo-full.yml` file,
so afterthat DLRN is able to get all required informations. <FIXME>


References
==========

.. [1] https://cbs.centos.org/
.. [2] https://github.com/softwarefactory-project/DLRN
.. [3] https://www.rdoproject.org/what/dlrn/
