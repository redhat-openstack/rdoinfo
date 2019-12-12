#!/usr/bin/env python
from __future__ import print_function
from distroinfo import info
import yaml
import requests
import sys

def verify(fn, include_fns=[]):
    inforepo = info.DistroInfo(
               info_files=[fn] + include_fns,
               local_info='.').get_info()
    # print(yaml.dump(inforepo))
    buildsystags = list_buildsys_tags(inforepo)
    for pkg in inforepo['packages']:
        verify_buildsys_tags(pkg, buildsystags)
        if 'distgit' in pkg:
            verify_url(pkg['distgit'])
        if 'master-distgit' in pkg:
            verify_url(pkg['master-distgit'])
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

def verify_url(url):
    r = requests.head(url)
    if r.status_code not in [200]:
        raise Exception("ERROR: %s returned %s\n%s\n%s", url, r, r.headers, r.content)

def list_buildsys_tags(info):
    tags = ['version-locked']
    for release in info['releases']:
        for repo in release['repos']:
            if 'buildsys-tags' in repo.keys():
                tags = tags + repo['buildsys-tags']
    return tags

if __name__ == '__main__':
    verify('rdo-full.yml')
