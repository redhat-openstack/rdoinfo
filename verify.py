#!/usr/bin/env python
from __future__ import print_function
from distroinfo import info
import yaml


def verify(fn, include_fns=[]):
    inforepo = info.DistroInfo(
               info_files=[fn] + include_fns,
               local_info='.').get_info()
    print(yaml.dump(inforepo))
    buildsystags = list_buildsys_tags(inforepo)
    for pkg in inforepo['packages']:
        verify_buildsys_tags(pkg, buildsystags)
    verify_components(inforepo)
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

def verify_components(info):
    # First, create list of components
    cmp_list = []
    for component in info['components']:
        cmp_list.append(component['name'])
    # Then, make sure all packages belong to a defined component
    for pkg in info['packages']:
        if 'component' in pkg:
            component = pkg['component']
            if component not in cmp_list:
                raise Exception("Package %s belongs to a non-existing "
                                "component %s" % (pkg['name'], component))

        # We can override components on a per-tag basis, check it
        if 'tags' in pkg:
            for tag in pkg['tags']:
                if pkg['tags'][tag] is not None:
                    if 'component' in pkg['tags'][tag]:
                        component = pkg['tags'][tag]['component']
                        if component not in cmp_list:
                            raise Exception("Package %s in tag %s belongs to "
                                            "a non-existing component %s" %
                                            (pkg['name'], tag, component))

def list_buildsys_tags(info):
    tags = ['version-locked']
    for release in info['releases']:
        for repo in release['repos']:
            if 'buildsys-tags' in repo.keys():
                tags = tags + repo['buildsys-tags']
    return tags

if __name__ == '__main__':
    verify('rdo-full.yml')
