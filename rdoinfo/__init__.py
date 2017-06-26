import collections
import copy
import six
import yaml
from os import path


__version__ = '0.2'

"""
rdoinfo module provides a set of methods to interact with
metadata files contained in the repository.
"""


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


class SubstitutionFailed(InvalidInfoFormat):
    msg_fmt = "Substitution failed for string: %(txt)s"


class DuplicatedProject(InvalidInfoFormat):
    msg_fmt = "Duplicated project: %(prj)s"


def include_packages(info, include_info):
    if include_info:
        if 'packages' in include_info.keys():
            info['packages'] = info['packages'] + include_info['packages']
        if 'package-configs' in include_info.keys():
            info['package-configs'].update(include_info['package-configs'])
    return info


def parse_info_file(fn, apply_tag=None, include_fns=['deps.yml']):
    """
    Parse rdoinfo metadata files.

    :param fn: name of main metadata file, as rdo.yml
    :param apply_tag: tag to apply
    :param include_fns: list of additional files to be parsed, defaults to deps.yml
    :returns: dictionary containing all packages in rdoinfo
    """
    info = yaml.load(open(fn, 'rb'))
    for fn in include_fns:
        include_file = path.join(path.dirname(fn), fn)
        include_info = yaml.load(open(include_file, 'rb'))
        info = include_packages(info, include_info)
    parse_info(info, apply_tag=apply_tag)
    return info

def parse_info(info, apply_tag=None):
    parse_releases(info)
    parse_packages(info, apply_tag=apply_tag)


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
    if 'package-default' not in info:
        info['package-default'] = {}
    if 'package-configs' not in info:
        info['package-configs'] = {}
    return info['package-default'], info['package-configs']


def substitute_package(pkg):
    # substitution is very simple, no recursion
    new_pkg = copy.copy(pkg)
    for key, val in pkg.items():
        if isinstance(val, six.string_types):
            try:
                new_pkg[key] = val % pkg
            except KeyError:
                raise SubstitutionFailed(txt=val)
    return new_pkg


def parse_package(pkg, info, apply_tag=None):
    pkddefault, pkgconfs = parse_package_configs(info)
    # start with default package config
    parsed_pkg = copy.deepcopy(pkddefault)
    if 'conf' in pkg:
        # apply package configuration template
        conf_id = pkg['conf']
        try:
            conf = pkgconfs[conf_id]
        except KeyError:
            raise UndefinedPackageConfig(conf=conf_id)
        parsed_pkg.update(conf)
    parsed_pkg.update(pkg)
    if apply_tag:
        tags = parsed_pkg.get('tags', {})
        tagdict = tags.get(apply_tag)
        if tagdict:
            parsed_pkg.update(tagdict)
    pkg = substitute_package(parsed_pkg)

    try:
        name = pkg['name']
    except KeyError:
        raise MissingRequiredItem(item='package.name')
    if 'project' not in pkg:
        raise MissingRequiredItem(
            item="project for '%s' package" % name)
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


def check_for_duplicates(pkg, pkgs):
    for oldpkg in pkgs:
        if pkg['name'] == oldpkg['name']:
            return True
    return False


def parse_packages(info, apply_tag=None):
    try:
        pkgs = info['packages']
    except KeyError:
        raise MissingRequiredSection(section='packages')
    if not isinstance(pkgs, collections.Iterable):
        raise InvalidInfoFormat(msg="'packages' section must be a list")

    parsed_pkgs = []
    for pkg in pkgs:
        parsed_pkg = parse_package(pkg, info, apply_tag=apply_tag)
        if check_for_duplicates(parsed_pkg, parsed_pkgs):
            raise DuplicatedProject(prj=parsed_pkg['name'])
        else:
            parsed_pkgs.append(parsed_pkg)

    info['packages'] = parsed_pkgs
