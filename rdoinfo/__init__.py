import copy
import collections
import yaml


__version__ = '0.1'


class RdoinfoException(Exception):
    msg_fmt = "An unknown error occurred"

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt % kwargs
            except Exception as e:
                message = self.msg_fmt
        super(RdoinfoException, self).__init__(msg)


class InvalidInfoFormat(RdoinfoException):
    msg_fmt = "Invalid info format."


class MissingRequiredSection(InvalidInfoFormat):
    msg_fmt = "Info is missing required section: %(section)s"


class MissingRequiredItem(InvalidInfoFormat):
    msg_fmt = "Required item missing: %(item)s"


class UndefinedPackageConfig(InvalidInfoFormat):
    msg_fmt = "Package config isn't defined: %(conf)s"


def parse_info_file(fn):
    info = yaml.load(open(fn, 'rb'))
    parse_info(info)
    return info


def parse_info(info):
    parse_releases(info)
    parse_packages(info)


def parse_release_repo(repo, default_branch=None):
    if 'name' not in repo:
        raise MissingRequiredItem(item='repo.name')
    if 'branch' not in repo:
        if default_branch:
            repo['branch'] = default_branch
        else:
            raise MissingRequiredItem(item='repo.branch')
    return repo


def parse_releases(info):
    try:
        releases = info['releases']
    except KeyError:
        raise MissingRequiredSection(section='releases')
    if not isinstance(releases, collections.Iterable):
        raise InvalidInfoFormat(msg="'releases' section must be a list")
    for rls in releases:
        try:
            rls_name = rls['name']
        except KeyError:
            raise MissingRequiredItem(item='release.name')
        try:
            repos = rls['repos']
        except KeyError:
            raise MissingRequiredItem(item='release.builds')
        default_branch = rls.get('branch')
        for repo in repos:
            parse_release_repo(repo, default_branch)
    # XXX: releases not yet used, subject to change
    return releases


def parse_package_configs(info):
    if 'package-configs' not in info:
        info['package-configs'] = {}
    return info['package-configs']


def apply_package_config(pkg, conf):
    new_pkg = copy.deepcopy(conf)
    new_pkg.update(pkg)
    return new_pkg


def substitute_package(pkg):
    # substitution is very simple, no recursion
    new_pkg = copy.copy(pkg)
    for key, val in pkg.items():
        if isinstance(val, basestring):
            new_pkg[key] = val % pkg
    return new_pkg


def parse_package(pkg, info):
    pkgconfs = parse_package_configs(info)
    if 'conf' in pkg:
        conf_id = pkg['conf']
        try:
            conf = pkgconfs[conf_id]
        except KeyError:
            raise UndefinedPackageConfig(conf=conf_id)
        pkg = apply_package_config(pkg, conf)
    pkg = substitute_package(pkg)
    try:
        name = pkg['name']
    except KeyError:
        raise MissingRequiredItem(item='package.name')
    try:
        maints = pkg['maintainers']
    except:
        raise MissingRequiredItem(
            item="maintainers for '%s' package" % name)
    if not maints:
        raise MissingRequiredItem(
            item="at least one maintainer for '%s' package" % name)
    try:
        for maint in maints:
            if '@' not in maint:
                raise InvalidInfoFormat(
                    msg="'%s' doesn't look like maintainer's email." % maint)
    except TypeError:
        raise InvalidInfoFormat(
            msg='package.maintainers must be a list of email addresses')

    return pkg


def parse_packages(info):
    try:
        pkgs = info['packages']
    except KeyError:
        raise MissingRequiredSection(section='packages')
    if not isinstance(pkgs, collections.Iterable):
        raise InvalidInfoFormat(msg="'packages' section must be a list")

    parsed_pkgs = []
    for pkg in pkgs:
        parsed_pkgs.append(parse_package(pkg, info))
    info['packages'] = parsed_pkgs
