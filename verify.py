#!/usr/bin/env python
from __future__ import print_function
import rdoinfo
import yaml


def verify(fn, include_fns=[]):
    info = rdoinfo.parse_info_file(fn, include_fns=include_fns)
    print(yaml.dump(info))
    buildsystags = list_buildsys_tags(info)
    for pkg in info['packages']:
        verify_buildsys_tags(pkg, buildsystags)
    print("\n%s looks OK" % fn)

def verify_buildsys_tags(pkg, buildsystags):
    if 'buildsys-tags' in pkg.keys():
        btags = pkg['buildsys-tags']
        for btag in btags.keys():
            if btag in buildsystags:
                value = btags[btag]
                if value is None and btag != 'version-locked':
                    raise Exception("buildsys-tag %s for package %s is empty" %
                                    (btag, pkg['name']))
            else:
                raise Exception("buildsys-tag %s for package %s does not exist" %
                                (btag, pkg['name']))
    return True

def list_buildsys_tags(info):
    tags = ['version-locked']
    for release in info['releases']:
        for repo in release['repos']:
            if 'buildsys-tags' in repo.keys():
                tags = tags + repo['buildsys-tags']
    return tags

if __name__ == '__main__':
    verify('rdo.yml', include_fns=['deps.yml'])
