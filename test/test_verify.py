from __future__ import print_function
import pytest
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from distroinfo import info


retry_strategy = Retry(
    total=3,
    backoff_factor=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)


broken_urls = """
https://github.com/rdo-common/UcsSdk
https://github.com/rdo-common/atomic
https://github.com/rdo-common/buildah
https://github.com/rdo-common/container-selinux
https://github.com/rdo-common/container-storage-setup
https://github.com/rdo-common/containernetworking-plugins
https://github.com/rdo-common/etcd
https://github.com/rdo-common/go-srpm-macros
https://github.com/rdo-common/golang
https://github.com/rdo-common/gtest
https://github.com/rdo-common/libseccomp
https://github.com/rdo-common/libsodium
https://github.com/rdo-common/libwebsockets
https://github.com/rdo-common/oci-systemd-hook
https://github.com/rdo-common/oci-umount
https://github.com/rdo-common/podman
https://github.com/rdo-common/python-backports-ssl_match_hostname
https://github.com/rdo-common/python-chardet
https://github.com/rdo-common/runc
https://github.com/rdo-common/slirp4netns
https://github.com/rdo-packages/os-log-merger-distgit
https://src.fedoraproject.org/rpms/python-XStatic-Angular-Schema-Form
https://src.fedoraproject.org/rpms/python-XStatic-objectpath
https://src.fedoraproject.org/rpms/python-XStatic-tv4
https://src.fedoraproject.org/rpms/python-appdirs
https://src.fedoraproject.org/rpms/python-django-discover-runner
https://src.fedoraproject.org/rpms/python-edengrid
https://src.fedoraproject.org/rpms/python-string_utils
https://src.fedoraproject.org/rpms/rdo-rpm-macros
https://src.fedoraproject.org/rpms/sphinxcontrib-apidoc
""".split()


def test_url(url):
    """Checks that URL returns 200 error code."""
    r = session.head(url)
    if r.status_code not in [200, 301, 302]:
        if url in broken_urls:
            pytest.skip("Fix known broken url: %s" % url)
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
