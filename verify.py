#!/usr/bin/env python
import rdoinfo
import yaml


def verify(fn):
    info = rdoinfo.parse_info_file(fn)
    print yaml.dump(info)
    print "\n%s looks OK" % fn


if __name__ == '__main__':
    verify('rdo.yml')
