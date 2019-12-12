from __future__ import print_function
import pytest
import requests
from distroinfo import info


# TODO(ssbarnea): Remove xfail as soon we resolve the broken URLs
@pytest.mark.xfail
def test_url(url):
    r = requests.head(url)
    if r.status_code not in [200, 301, 302]:
        raise Exception(
            "ERROR: %s returned %s\n%s\n%s",
            url, r, r.headers, r.content)


def pytest_generate_tests(metafunc):

    if 'url' in metafunc.fixturenames:

        fn = 'rdo-full.yml'
        include_fns = []

        inforepo = info.DistroInfo(
            info_files=[fn] + include_fns, local_info='.').get_info()
        buildsystags = list_buildsys_tags(inforepo)

        urls = set()
        for pkg in inforepo['packages']:
            verify_buildsys_tags(pkg, buildsystags)
            for x in ['distgit', 'master-distgit']:
                if x in pkg:
                    urls.add(pkg[x])
        metafunc.parametrize("url", urls)
        verify_components(inforepo)


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
                raise Exception(
                    "buildsys-tag %s for package %s does not exist" %
                    (btag, pkg['name']))
    return True


def list_buildsys_tags(info):
    tags = ['version-locked']
    for release in info['releases']:
        for repo in release['repos']:
            if 'buildsys-tags' in repo.keys():
                tags = tags + repo['buildsys-tags']
    return tags
