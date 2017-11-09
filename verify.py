#!/usr/bin/env python
from __future__ import print_function
import argparse
from functools import cmp_to_key

import rdoinfo
from rdopkg.utils.specfile import split_filename
import six
import yaml

try:
    import rpm
    HAS_RPM = True
except:
    HAS_RPM = False

if six.PY3:
    def cmp(left, right):
        return((left > right) - (left < right))

def _cmp_buildsys_tags(tag1, tag2):
    """Compare buildsys-tags

    Buildsys-tags scheme: cloud7-openstack-<release>-<stage>
    Release can be sorted according a lexicographic order
    Stage are candidate, testing, release

    So ordering common, pike, queens should give
    common-release -> common-testing -> common-candidate ->
    pike-release -> pike-testing -> pike-candidate
    -> queens-testing -> queens-candidate
    """
    release_weight = {'candidate': 3, 'testing': 2, 'release': 1}
    release1, stage1 = tag1.replace('cloud7-openstack-', '').split('-')
    release2, stage2 = tag2.replace('cloud7-openstack-', '').split('-')
    if release1 == release2:
        return cmp(release_weight[stage1], release_weight[stage2])
    return cmp(release1, release2)


def _order_buildsys_tags(buildsystags):
    """Order list of buildsys tags
    """
    # Not useful in our context
    buildsystags.remove('version-locked')
    # preliminary sort
    result = sorted(buildsystags, key=cmp_to_key(_cmp_buildsys_tags))
    return result


def _convert_nvr_to_rpm_hdr(nvr):
    """Convert NVR to RPM header
    """
    hdr = rpm.hdr()
    name, version, release, _, _ = split_filename(nvr)
    hdr[rpm.RPMTAG_NAME] = name
    hdr[rpm.RPMTAG_VERSION] = version
    hdr[rpm.RPMTAG_RELEASE] = release
    # TODO(hguemar): use epoch?
    return hdr


def _compare_nvr(nvr1, nvr2):
    """Compare NVR using rpm
    """
    hdr1 = _convert_nvr_to_rpm_hdr(nvr1)
    hdr2 = _convert_nvr_to_rpm_hdr(nvr2)
    return rpm.versionCompare(hdr1, hdr2)


def _verify_upgrade_path(info, buildsystags):
    """Check potential upgrade path issues
    """
    buildsystags = _order_buildsys_tags(buildsystags)
    for package in info['packages']:
        if 'buildsys-tags' not in package:
            continue
        previous, current = None, None
        for buildsystag in buildsystags:
            if buildsystag in package['buildsys-tags']:
                current = buildsystag
                if previous is not None:
                    previous_package = package['buildsys-tags'][previous]
                    current_package = package['buildsys-tags'][current]
                    res = _compare_nvr(previous_package, current_package)
                    if res == 1:
                        print(
"""=== WARNING (potential break in upgrade path from {0} to {1}) ===
{2} is newer than {3}
""".format(previous, current, previous_package, current_package))
                previous = current
    import sys
    sys.exit(0)


def verify(fn, include_fns=[], upgrade_path=False):
    info = rdoinfo.parse_info_file(fn, include_fns=include_fns)
    buildsystags = list_buildsys_tags(info)
    if upgrade_path and HAS_RPM:
        _verify_upgrade_path(info, buildsystags)
    print(yaml.dump(info))
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


def main():
    parser = argparse.ArgumentParser(description='Check rdoinfo consistency')
    parser.add_argument('--upgrade-path', help='Check upgrade path',
                        action='store_true')
    args = parser.parse_args()
    verify('rdo.yml', include_fns=['deps.yml'],
           upgrade_path=args.upgrade_path)


if __name__ == '__main__':
    main()
