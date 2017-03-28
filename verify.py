#!/usr/bin/env python
from __future__ import print_function
import rdoinfo
import yaml


def verify(fn):
    info = rdoinfo.parse_info_file(fn, deps=True)
    print(yaml.dump(info))
    cbstags = list_cbs_tags(info)
    for pkg in info['packages']:
        verify_cbs_tags(pkg, cbstags)
    print("\n%s looks OK" % fn)

def verify_cbs_tags(pkg, cbstags):
    if 'cbs-tags' in pkg.keys():
        reltags = pkg['cbs-tags']
        for reltag in reltags.keys():
            for tag in reltags[reltag].keys():
                try:
                    cbstags[reltag][tag]
                except Exception as ex:
                    raise Exception("cbs-tag %s/%s for package %s does not exist" %
                                    (reltag, tag, pkg['name']))
                value = reltags[reltag][tag]
                if value is None:
                    raise Exception("cbs-tag %s/%s for package %s is empty" %
                                    (reltag, tag, pkg['name']))
    return True

def list_cbs_tags(info):
    tags = {}
    for release in info['releases']:
        if 'cbs-tags' in release.keys():
            reltags = {release['name']: release['cbs-tags']}
            tags.update(reltags)
    return tags

if __name__ == '__main__':
    verify('rdo.yml')
