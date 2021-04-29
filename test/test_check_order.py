import os
import pytest
import yaml


def test_is_projects_sorted_in_buildsys_tags_files():
    path = 'buildsys-tags'
    files = [f for f in os.listdir(path) if os.path.isfile(path + '/' + f)]
    for f in files:
        projects = get_projects_from_buildsys_tags_file(path + '/' + f)
        assert projects == sorted(projects), "Projects are not well sorted"


def get_projects_from_buildsys_tags_file(file):
    projects = list()
    with open(file, 'r') as stream:
        data = yaml.safe_load(stream)
    if 'packages' in data.keys():
        if data['packages'] is not None:
            for pkg in data['packages']:
                projects.append(pkg['project'])
    return projects
