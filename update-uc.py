#!/usr/bin/env python
#
# Update OpenStack Oslo and Clients libraries versions in rdoinfo from:
# * master branch (default)
# curl -OJ http://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=master
# * stable/ocata
# curl -OJ http://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=stable/ocata

# USAGE
#    update-uc.py [branch]
# If branch is not specified, master i.e. currently ocata-uc is assumed.

import copy
import ruamel.yaml as yaml
import sys

RDO = 'rdo.yml'
SOURCE_BRANCH = 'source-branch'
UC = 'upper-constraints.txt'
if len(sys.argv) > 1:
    UC_RELEASE = sys.argv[1]
else:
    UC_RELEASE = 'stein-uc'


# filter for Oslo and clients
def filter_oslo_clients(project):
    return project.startswith('oslo') or \
           project.endswith('client') or \
           project == 'osc-lib'


def filter_all(project):
    return True


def filter_all_minus_tripleo(project):
    TRIPLEO_PROJECTS = [
      'diskimage-builder',
      'os-apply-config',
      'os-collect-config',
      'os-net-config',
      'os-refresh-config',
      'tripleo-common',
      'mistral',
      'tempest',
      'instack-undercloud',
      'paunch',
    ]
    return project not in TRIPLEO_PROJECTS


# load and filter upper-constraints.txt
# normalize project name for rdoinfo
def load_uc(projects_filter):
    uc = {}
    with open(UC, 'rb') as ucfile:
        for line in ucfile.readlines():
            name, version_spec = line.rstrip().split('===')
            if name and projects_filter(name):
                version = version_spec.split(';')[0]
                if version:
                    if name.startswith('python-'):
                        name = name[7:]
                    uc[name.replace('.', '-')] = version
    return uc


def update_uc():
    # uc = load_uc(filter_oslo_clients)
    uc = load_uc(filter_all_minus_tripleo)
    uc_projects = uc.keys()

    with open(RDO, 'rb') as infile:
        info = yaml.load(infile, Loader=yaml.RoundTripLoader)
    DEFAULT_RELEASES = info['package-default']['tags']
    RELEASES_PUPPET = info['package-configs']['rpmfactory-puppet']['tags']
    for pkg in info['packages']:
        project = pkg['project']
        if project in uc_projects:
            new_version = uc[project]
            # "Setting %s to version %s" % (project, new_version)
            if 'tags' in pkg:
                tags = pkg['tags']
                if 'version-locked' in tags or 'under-review' in tags:
                    print("Not updating %s, it is version-locked or under"
                          " review" % project)
                    continue
                prev_version = tags.get(UC_RELEASE)
                if prev_version:
                    prev_version = prev_version.get(SOURCE_BRANCH)
            else:
                if project.startswith('puppet'):
                    tags = copy.copy(RELEASES_PUPPET)
                else:
                    tags = copy.copy(DEFAULT_RELEASES)
                prev_version = None
            if 'tags' in pkg and UC_RELEASE not in pkg['tags']:
                print("Not updating %s, it is not included in release %s"
                      % (project, UC_RELEASE))
                continue
            tags[UC_RELEASE] = {SOURCE_BRANCH: new_version}
            if prev_version:
                if prev_version != new_version:
                    print("%s updated from %s to %s" %
                          (project, prev_version, new_version))
                else:
                    print("%s %s already up to date" %
                          (project, new_version))
            else:
                print("%s first time pin to %s" %
                      (project, new_version))

            pkg['tags'] = tags
            uc_projects.remove(project)
        else:
            # "%s not found in upper-constraints" % project
            pass

    # "Projects not in rdoinfo: %s" % string.join(uc_projects, ' ')

    with open(RDO, 'w') as outfile:
        outfile.write(yaml.dump(info, Dumper=yaml.RoundTripDumper, indent=2))


if __name__ == '__main__':
    update_uc()

